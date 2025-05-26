function toggleCollapse(event) {
    var target_id = event.target.getAttribute("collapse-target")
    if (target_id === null) {
        return
    }
    var target = document.getElementById(target_id)
    if (target === null) {
        return
    }
    if (target.classList.contains("collapse")) {
        target.classList.remove("collapse")
    } else {
        target.classList.add("collapse")
    }
}

function addCollapse() {
    var collapse_buttons = document.querySelectorAll("[collapse-target]")
    for (var button of collapse_buttons) {
        button.setAttribute("onclick", "toggleCollapse(event)")
    }
}

window.addEventListener("DOMContentLoaded", addCollapse, false)