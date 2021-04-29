/**
 * Auto Refresh component
 * @param url
 * @param delay (in seconds)
 * @returns {{init(*): void, submit(): Promise<void>, interval: null, refreshedHtml: null}}
 * @constructor
 *
 * Usage:
 *
 * <div x-data="AutoRefresh('/some/url', 5)" x-init="init()" x-html="refreshedHtml || $el.innerHTML">
 *     <p>This content will be refreshed</p>
 * </div>
 */
function AutoRefresh(url, delay) {
    return {
        interval: null,
        refreshedHtml: null,
        init($el) {
            this.refreshedHtml = $el.innerHTML;
            this.interval = setInterval(this.submit.bind(this), delay * 1000);
        },
        async submit() {
            try {
                const response = await fetch(url, {
                    method: 'GET',
                    headers: {
                        "Accepts": "text/html",
                        "X-CSRFToken": document.cookie
                            .split('; ')
                            .find(row => row.startsWith('csrftoken='))
                            .split('=')[1]
                    },
                });
                this.refreshedHtml = await response.text();
            } catch (e) {
                console.error(`Error while submitting form: ${e}`);
            } finally {
                clearInterval(this.interval);
            }
        },
    }
}

/**
 * Editable Card component
 * @param url
 * @returns {{init(*): void, submit(): Promise<void>, interval: null, refreshedHtml: null}}
 * @constructor
 *
 * Usage:
 *
 * <div x-data="AutoRefresh('/some/url', 5)" x-init="init()" x-html="refreshedHtml || $el.innerHTML">
 *     <p>This content will be refreshed</p>
 * </div>
 */
function Updatable(url) {
    return {
        editing: [],
        updates: {},
        updated: false,
        update(key, value) {
            this.updates[key] = value;
            this.updated = true;
        },
        async submit() {
            try {
                const response = await fetch(url, {
                    method: 'POST',
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": document.cookie
                            .split('; ')
                            .find(row => row.startsWith('csrftoken='))
                            .split('=')[1]
                    },
                    body: JSON.stringify(this.updates)
                });
                this.$el.innerHTML = await response.text();
                this.updated = false;
            } catch (e) {
                console.error(`Error while submitting form: ${e}`);
            }
        },
    }
}

function Editable(key, value, originalValue) {
    return {
        key,
        value,
        originalValue,
        editing: false,
        isChanged() {
            return this.value !== "" && this.value !== originalValue;
        },
        displayedValue() {
            return this.value !== "" ?
                this.value :
                (originalValue !== "" ? originalValue : "-");
        },
        toggle() {
            this.editing = !this.editing;
            if (this.editing) {
                setTimeout(() => {
                    this.$refs.input.focus();
                    this.$refs.input.setSelectionRange(10000, 10000);
                }, 100)
            }
        },
    }
}