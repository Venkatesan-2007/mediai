/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        "./src/**/*.{js,jsx,ts,tsx}",
        "./public/index.html"
    ],
    theme: {
        extend: {
            colors: {
                pink: {
                    50: '#fdf2f8',
                    100: '#fce7f3',
                    200: '#fbcfe8',
                    300: '#f9a8d4',
                    400: '#f472b6',
                    500: '#ec4899',
                    600: '#db2777',
                    700: '#be185d',
                    800: '#9d174d',
                    900: '#831843',
                },
                healthcare: {
                    pink: '#ffb6c1',
                    light: '#fff0f5',
                    soft: '#ffe4e9',
                    dark: '#e91e63',
                    muted: '#f8bbd0',
                }
            },
            fontFamily: {
                sans: ['Poppins', 'Inter', 'sans-serif'],
            },
            boxShadow: {
                'glass': '0 8px 32px 0 rgba(255, 182, 193, 0.37)',
                'soft': '0 4px 15px rgba(233, 30, 99, 0.15)',
                'card': '0 10px 40px rgba(233, 30, 99, 0.1)',
            },
            backgroundImage: {
                'gradient-pink': 'linear-gradient(135deg, #fff0f5 0%, #ffe4e9 50%, #fce7f3 100%)',
                'gradient-ai': 'linear-gradient(135deg, #fdf2f8 0%, #fce7f3 50%, #fbcfe8 100%)',
            },
            animation: {
                'float': 'float 6s ease-in-out infinite',
                'pulse-slow': 'pulse 3s ease-in-out infinite',
            },
            keyframes: {
                float: {
                    '0%, 100%': { transform: 'translateY(0)' },
                    '50%': { transform: 'translateY(-10px)' },
                }
            }
        },
    },
    plugins: [],
}
