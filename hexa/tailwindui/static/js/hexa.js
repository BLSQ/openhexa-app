/**
 * Auto Refresh component
 * @param url
 * @param delay (in seconds)
 * @returns {{init(): void, submit(): Promise<void>, interval: null, refreshedHtml: null}}
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
            }
        },
    }
}