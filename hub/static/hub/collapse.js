function toggleCollapse(target_id) {
    console.log("Click " + target_id)
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
        let target_id = button.getAttribute("collapse-target")
        button.addEventListener("click", function() {
            toggleCollapse(target_id)
        })
    }
}

window.addEventListener("DOMContentLoaded", addCollapse, false)
document.addEventListener("htmx:afterRequest", addCollapse, false)