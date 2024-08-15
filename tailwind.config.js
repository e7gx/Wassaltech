module.exports = {
    content: [
      "./templates/**/*.{html,js}",
      "./static/**/*.{js,css}",
      "./**/templates/**/*.{html,js}",
      "./**/static/**/*.{js,css}",
    ],
    theme: {
      extend: {},
    },
    plugins: [require("daisyui")],
    daisyui: {
      themes: ["light", "dark"],
    },
  }
