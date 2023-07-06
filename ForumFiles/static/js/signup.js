signup_imgInput.onchange = evt => {
  const [file] = signup_imgInput.files
  if (file) {
    signup_chosen_avatar.src = URL.createObjectURL(file)
  }
}