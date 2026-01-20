/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                primary: "#1a73e8", // Google Blue
                secondary: "#e8eaed",
                dark: "#202124",
                "dark-surface": "#2d2e31"
            }
        },
    },
    plugins: [],
}
