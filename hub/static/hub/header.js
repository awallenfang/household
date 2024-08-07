function toggleQuickspace(e) {
    console.log("Yes")
    console.log(e.target)
    let dropdown = document.getElementsByClassName("quick-space-container")[0]

    if (dropdown.style.display == "none") {
        dropdown.style.display = "flex"
    } else {
        dropdown.style.display = "none"

    }
}