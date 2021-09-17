function QuickSearch(advancedSearchUrl) {
    const MODE_WAITING_FOR_INPUT = 'MODE_WAITING_FOR_INPUT';
    const MODE_BUSY = 'MODE_BUSY';
    const MODE_NO_RESULTS = 'MODE_NO_RESULTS';
    const MODE_RESULTS = 'MODE_RESULTS';

    let abortController = null;

    return {
        MODE_BUSY,
        MODE_RESULTS,
        MODE_NO_RESULTS,
        MODE_WAITING_FOR_INPUT,
        expanded: false,
        query: "",
        mode: MODE_WAITING_FOR_INPUT,
        results: [],
        expand() {
            this.expanded = true;
            bodyScrollLock.disableBodyScroll(this.$refs.modalContent);
            setTimeout(() => this.$refs.input.focus(), 100);
        },
        collapse() {
            this.expanded = false
            bodyScrollLock.enableBodyScroll(this.$refs.modalContent);
        },
        toggle() {
            this.expanded ? this.collapse() : this.expand()
        },
        switchToAdvancedSearch($event) {
            $event.preventDefault();
            window.location.href = `${advancedSearchUrl}?query=${this.query}`;
        },
        async check() {
            if (this.query.length >= 3) {
                await this.submit();
            } else {
                this.waitForInput();
            }
        },
        async submit() {
            if (abortController !== null) {
                abortController.abort();
            }
            abortController = new AbortController();
            this.mode = MODE_BUSY;
            this.results = [];
            try {
                const response = await fetch(`${this.$refs.form.action}?query=${this.query}`, {
                    method: this.$refs.form.method,
                    headers: {'Content-Type': 'application/json'},
                    signal: abortController.signal
                });
                const responeData = await response.json();
                this.results = responeData.results;
                const newMode = this.results.length > 0 ? MODE_RESULTS : MODE_NO_RESULTS;
                this.mode = newMode;
                abortController = null;
            } catch (e) {
                if (e.message.includes("abort")) {
                    console.info("Aborting")
                } else {
                    console.error(`Error while submitting search: ${e}`);
                }
            }
        },
        waitForInput() {
            console.log(`Waiting for input`);

            this.mode = MODE_WAITING_FOR_INPUT;
            this.results = [];
        },
    }
}

/**
 * Auto Refresh component
 * @param url
 * @param delay (in seconds)
 * @returns {{init(*): void, submit(): Promise<void>, interval: null, refreshedHtml: null}}
 * @constructor
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
 * Updatable component
 * @param url
 * @returns {{init(*): void, submit(): Promise<void>, interval: null, refreshedHtml: null}}
 * @constructor
 */
function Updatable(url) {
    console.log(`Creating Updatable (url: ${url})`);

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

/**
 * Editable component
 *
 * @param key
 * @param value
 * @param originalValue
 * @returns {{isChanged(): *, displayedValue(): *|string, originalValue, toggle(): void, value: *, key, editing: boolean}|boolean|*|string}
 * @constructor
 */
function Editable(key, value, originalValue) {
    return {
        key,
        // TODO: check
        // value,
        value: value !== "" ? value : originalValue,
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

/**
 * Commentable component
 *
 * @param url
 * @param indexId
 * @returns {{cancel(*): void, submit(*): Promise<void>, startCommenting(*): void, text: string, commenting: boolean}}
 * @constructor
 */
function Commentable(url, indexId) {
    console.log(`Creating Commentable (url: ${url}, indexId: ${indexId})`);

    return {
        text: "",
        commenting: false,
        startCommenting($event) {
            this.commenting = $event.target.value !== "";
        },
        cancel($event) {
            this.text = "";
            this.commenting = false;
            $event.target.blur();
        },
        async submit($event) {
            $event.preventDefault();
            try {
                let formData = new FormData();
                formData.append("text", this.text);
                formData.append("index", indexId);

                const response = await fetch(url, {
                    method: 'POST',
                    headers: {
                        "X-CSRFToken": document.cookie
                            .split('; ')
                            .find(row => row.startsWith('csrftoken='))
                            .split('=')[1]
                    },
                    body: formData
                });
                const responseText = await response.text();
                const newContent = document.createElement("div");
                newContent.innerHTML = responseText;
                this.$refs['form-container'].after(newContent.querySelector("li"));
                this.text = "";
                $event.target.blur();
            } catch (e) {
                console.error(`Error while submitting form: ${e}`);
            }
        },
    }
}


/**
 * CardSection component
 *
 * @param url
 * @param contentTypeKey
 * @param objectId
 * @returns {{cancel(*): void, submit(*): Promise<void>, startCommenting(*): void, text: string, commenting: boolean}}
 * @constructor
 */
function CardSection(url, contentTypeKey, objectId) {
    return {
        editing: false,
        toggle($event) {
            this.editing = !this.editing
        },
    }
}

function TomSelectable(multiple = true) {
    return {
        init($el) {
            new TomSelect($el, {
                optionClass: 'option',
                itemClass: 'item',
                render: {
                    option: function (data, escape) {
                        return '<div>' + escape(data.text) + '</div>';
                    },
                    item: function (data, escape) {
                        return '<div>' + escape(data.text) + '</div>';
                    },
                    option_create: function (data, escape) {
                        return '<div class="create">Add <strong>' + escape(data.input) + '</strong>&hellip;</div>';
                    },
                    no_results: function (data, escape) {
                        return '<div class="no-results">No results found for "' + escape(data.input) + '"</div>';
                    },
                    not_loading: function (data, escape) {
                        // no default content
                    },
                    optgroup: function (data) {
                        let optgroup = document.createElement('div');
                        optgroup.className = 'optgroup';
                        optgroup.appendChild(data.options);
                        return optgroup;
                    },
                    optgroup_header: function (data, escape) {
                        return '<div class="optgroup-header">' + escape(data.label) + '</div>';
                    },
                    loading: function (data, escape) {
                        return '<div class="spinner"></div>';
                    },
                    dropdown: function () {
                        return '<div></div>';
                    }
                }
            })
        }
    }
}

// TODO: should be placed in s3 app
function S3Upload(getUploadUrl, syncUrl, prefix="") {
    return {
        refreshedHtml: null,
        uploading: false,
        init($el) {
            this.refreshedHtml = $el.innerHTML;
        },
        async onChange() {
            this.uploading = true;
            const uploadedFile = this.$refs.input.files[0];
            const fileName = uploadedFile.name;

            // Get presigned upload URL
            const signedUrlResponse = await fetch(`${getUploadUrl}?object_key=${prefix}${fileName}`, {
                method: this.$refs.form.method,
                headers: {
                    'Content-Type': 'text/plain',
                    "X-CSRFToken": document.cookie
                        .split('; ')
                        .find(row => row.startsWith('csrftoken='))
                        .split('=')[1]
                },
            });
            if (signedUrlResponse.status !== 201) {
                console.error(`Error when generating presigned URL (code: ${signedUrlResponse.status})`);
                return;
            }
            const preSignedUrl = await signedUrlResponse.text();

            // Upload file
            const uploadResponse = await fetch(preSignedUrl, {
                method: "PUT",
                headers: {
                    "Content-Type": uploadedFile.type,
                },
                body: uploadedFile
            });
            if (uploadResponse.status !== 200) {
                console.error(`Error when uploading file to S3 (code: ${uploadResponse.status})`);
                return;
            }

            // Sync & refresh section
            const refreshedResponse = await fetch(syncUrl, {
                method: "GET",
            });
            if (refreshedResponse.status !== 200) {
                console.error(`Error when refreshing after sync (code: ${refreshedResponse.status})`);
                return;
            }
            const frag = document.createElement("div");
            frag.innerHTML = await refreshedResponse.text();
            const swap = frag.querySelector("[x-swap=objects_section]");
            this.refreshedHtml = swap.innerHTML;
            this.uploading = false;
        }
    }
}
