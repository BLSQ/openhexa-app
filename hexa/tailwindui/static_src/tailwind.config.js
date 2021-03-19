const defaultTheme = require('tailwindcss/defaultTheme')

module.exports = {
    purge: [],  // TODO: https://github.com/timonweb/django-tailwind#purgecss-setup
    darkMode: false, // or 'media' or 'class'
    theme: {
        extend: {
            fontFamily: {
                sans: ['Inter var', ...defaultTheme.fontFamily.sans],
            },
        },
    },
    variants: {
        extend: {},
    },
    plugins: [
        require('@tailwindcss/forms'),
        require('@tailwindcss/typography'),
        require('@tailwindcss/aspect-ratio'),
    ],
}
