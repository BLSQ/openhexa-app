// Behaviour of the "Copy workspace" admin form: field toggles, search pickers
// for this server, and the values remembered between copies.
(function () {
    "use strict";

    const config = JSON.parse(document.getElementById("copier-config").textContent);
    const form = document.getElementById("copy-workspace-form");

    const FORM_KEY = "workspaceCopier.form";
    const SESSION_KEY = "workspaceCopier.session";
    const CUSTOM_SERVER = "custom";
    const SIDES = ["source", "target"];
    // The slugs and the new workspace's name are left out: they change with
    // every copy, and a stale one would silently target the wrong workspace.
    const REMEMBERED_FIELDS = [
        "source_server",
        "source_url",
        "target_server",
        "target_url",
        "target_mode",
        "target_organization",
        "resources",
        "all_dataset_versions",
        "include_connection_secrets",
    ];
    const PICKERS = [
        { field: "source_slug", side: "source", kind: "workspace" },
        { field: "target_workspace_slug", side: "target", kind: "workspace" },
        { field: "target_organization", side: "target", kind: "organization" },
    ].map(createPicker);

    // Storage can be unavailable (private browsing, blocked by policy); the
    // form must keep working without it.
    function load(storage, key) {
        try {
            return JSON.parse(storage.getItem(key)) || {};
        } catch (error) {
            return {};
        }
    }

    function store(storage, key, value) {
        try {
            storage.setItem(key, JSON.stringify(value));
        } catch (error) {
            // Nothing is remembered; the copy itself is unaffected.
        }
    }

    function forget(storage, key) {
        try {
            storage.removeItem(key);
        } catch (error) {
            // Nothing was stored.
        }
    }

    function checkboxes(name) {
        return Array.from(form.querySelectorAll('input[type="checkbox"][name="' + name + '"]'));
    }

    function readField(name) {
        if (name === "resources") {
            return checkboxes(name)
                .filter((box) => box.checked)
                .map((box) => box.value);
        }
        const element = form.elements[name];
        return element.type === "checkbox" ? element.checked : element.value;
    }

    function writeField(name, value) {
        if (name === "resources") {
            checkboxes(name).forEach((box) => {
                // Mandatory copiers are rendered checked and locked.
                if (!box.disabled) box.checked = value.includes(box.value);
            });
            return;
        }
        const element = form.elements[name];
        if (element.type === "checkbox") {
            element.checked = Boolean(value);
        } else {
            element.value = value;
        }
    }

    function isThisServer(side) {
        return form.elements[side + "_server"].value === "";
    }

    function serverKey(side) {
        const server = form.elements[side + "_server"].value;
        if (server === CUSTOM_SERVER) return form.elements[side + "_url"].value.trim();
        return server || "this-server";
    }

    // A resource's nested options only mean something when that resource is
    // copied: disabling them keeps them out of the POST, so the backend can't
    // receive an option for a copier that never runs.
    function syncResourceOptions() {
        form.querySelectorAll(".copier-resources > li").forEach((item) => {
            const box = item.querySelector('input[name="resources"]');
            item.querySelectorAll(".copier-option").forEach((option) => {
                option.classList.toggle("is-disabled", !box.checked);
                option.querySelectorAll("input").forEach((input) => {
                    input.disabled = !box.checked;
                });
            });
        });
    }

    function syncTargetMode() {
        const existing = form.elements["target_mode"].value === "existing";
        document.getElementById("target-mode-new-fields").hidden = existing;
        document.getElementById("target-mode-existing-fields").hidden = !existing;
    }

    function syncServer(side) {
        const custom = form.elements[side + "_server"].value === CUSTOM_SERVER;
        document.getElementById(side + "-custom-url").hidden = !custom;
        // A hidden invalid URL would block the submit with an error the
        // browser has nowhere to show; disabled, it is neither checked nor sent.
        form.elements[side + "_url"].disabled = !custom;
        PICKERS.filter((picker) => picker.side === side).forEach((picker) => picker.sync());
    }

    function serverPairKey() {
        return SIDES.map(serverKey).join(" ");
    }

    function syncSslWarning() {
        document.getElementById("copier-ssl-warning").hidden =
            !form.elements["disable_ssl_verification"].checked;
    }

    // The fields hold a slug or a UUID, the pickers show a name. Remembering
    // the names lets a restored value be shown as it was picked.
    const labels = load(localStorage, FORM_KEY).labels || {};

    // On this server a field becomes the admin's own search widget (select2),
    // fed by the lookup view. The text input stays in the form and receives the
    // picked value, so the backend sees the same field either way; on another
    // server, whose workspaces cannot be listed from here, it is typed into.
    function createPicker(lookup) {
        const input = form.elements[lookup.field];
        const $ = window.django.jQuery;
        let select = null;

        function enable() {
            const value = input.value.trim();
            select = document.createElement("select");
            select.id = input.id + "_picker";
            if (value) select.add(new Option(labels[value] || value, value, true, true));
            // A hidden required input would block the submit with an error
            // the browser has nowhere to show.
            select.required = input.required;
            input.required = false;
            input.hidden = true;
            input.after(select);
            $(select)
                .select2({
                    ajax: {
                        url: config.lookupUrl,
                        dataType: "json",
                        delay: 250,
                        data: (params) => ({ kind: lookup.kind, q: params.term || "" }),
                    },
                    theme: "admin-autocomplete",
                    width: "32em",
                    allowClear: !select.required,
                    placeholder: "",
                })
                // select2 raises its events through jQuery only.
                .on("change", () => {
                    const picked = select.selectedOptions[0];
                    input.value = picked ? picked.value : "";
                    if (picked) labels[picked.value] = picked.text;
                });
        }

        function disable() {
            $(select).select2("destroy");
            input.required = select.required;
            input.hidden = false;
            select.remove();
            select = null;
        }

        return {
            side: lookup.side,
            sync: function () {
                if (isThisServer(lookup.side) && !select) enable();
                if (!isThisServer(lookup.side) && select) disable();
            },
        };
    }

    // Tokens are remembered per side and server. A token saved for the other
    // side of the same server is the next best guess: one service account
    // often serves both.
    // Only a token this function filled in is ever replaced: one the operator
    // typed stays. An edit of the custom URL (keepUnmatched) also keeps a
    // filled token that has no match, so fixing a typo in the URL doesn't lose
    // the token saved under the mistyped one; picking another server clears
    // it, as it belongs to the previous server.
    const filledTokens = {};

    function fillToken(side, keepUnmatched) {
        const input = form.elements[side + "_token"];
        if (input.value && input.value !== filledTokens[side]) return;
        const tokens = load(sessionStorage, SESSION_KEY).tokens || {};
        const other = side === "source" ? "target" : "source";
        const key = serverKey(side);
        const token = tokens[side + "|" + key] || tokens[other + "|" + key] || "";
        if (!token && keepUnmatched) return;
        input.value = token;
        filledTokens[side] = token;
    }

    // Disabling SSL verification is remembered for the pair of servers it was
    // chosen for, so it never carries over to a copy between other servers.
    // A box the operator ticked by hand is left alone.
    let sslFilled = false;

    function fillSsl() {
        const box = form.elements["disable_ssl_verification"];
        const pairs = load(sessionStorage, SESSION_KEY).sslDisabledFor || {};
        if (pairs[serverPairKey()]) {
            sslFilled = sslFilled || !box.checked;
            box.checked = true;
        } else if (sslFilled) {
            box.checked = false;
            sslFilled = false;
        }
        syncSslWarning();
    }

    function remember() {
        const values = {};
        REMEMBERED_FIELDS.forEach((name) => {
            values[name] = readField(name);
        });
        const organization = values.target_organization.trim();
        const name = labels[organization];
        store(localStorage, FORM_KEY, {
            values: values,
            labels: name ? { [organization]: name } : {},
        });

        const session = load(sessionStorage, SESSION_KEY);
        const tokens = session.tokens || {};
        SIDES.forEach((side) => {
            const token = form.elements[side + "_token"].value;
            if (token) tokens[side + "|" + serverKey(side)] = token;
        });
        const sslDisabledFor = session.sslDisabledFor || {};
        if (readField("disable_ssl_verification")) {
            sslDisabledFor[serverPairKey()] = true;
        } else {
            delete sslDisabledFor[serverPairKey()];
        }
        store(sessionStorage, SESSION_KEY, {
            tokens: tokens,
            sslDisabledFor: sslDisabledFor,
        });
    }

    function restore() {
        const values = load(localStorage, FORM_KEY).values || {};
        REMEMBERED_FIELDS.forEach((name) => {
            if (name in values) writeField(name, values[name]);
        });
        SIDES.forEach((side) => fillToken(side));
        fillSsl();
    }

    if (config.restore) restore();

    SIDES.forEach((side) => {
        form.elements[side + "_server"].addEventListener("change", () => {
            syncServer(side);
            fillToken(side);
            fillSsl();
        });
        form.elements[side + "_url"].addEventListener("change", () => {
            fillToken(side, true);
            fillSsl();
        });
        syncServer(side);
    });
    checkboxes("resources").forEach((box) => box.addEventListener("change", syncResourceOptions));
    form.querySelectorAll('input[name="target_mode"]').forEach((radio) => {
        radio.addEventListener("change", syncTargetMode);
    });
    form.elements["disable_ssl_verification"].addEventListener("change", () => {
        sslFilled = false;
        syncSslWarning();
    });
    form.addEventListener("submit", remember);
    document.getElementById("copier-forget").addEventListener("click", () => {
        forget(localStorage, FORM_KEY);
        forget(sessionStorage, SESSION_KEY);
        // Not reload(): after a validation error that would re-submit the form.
        window.location.assign(window.location.pathname);
    });

    syncResourceOptions();
    syncTargetMode();
    syncSslWarning();
})();
