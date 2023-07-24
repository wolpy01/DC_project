if (window.location.pathname == '/profile/edit/') {
    settings_imgInput.onchange = evt => {
        const [file] = settings_imgInput.files
        if (file) {
            settings_chosen_avatar.src = URL.createObjectURL(file)
        }
    }
}
else {
    signup_imgInput.onchange = evt => {
        const [file] = signup_imgInput.files
        if (file) {
            signup_chosen_avatar.src = URL.createObjectURL(file)
        }
    }
}