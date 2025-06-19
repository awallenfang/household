function toggleCollapse(target_id, event) {
    if (target_id === null) {
        return
    }
    var target = document.getElementById(target_id)
    if (target === null) {
        return
    }
    console.log(event.target.nodeName)
    if (event.target.classList.contains("button") || event.target.nodeName === "INPUT") {
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
        button.addEventListener("click", function(e) {
            toggleCollapse(target_id, e)
        })
    }
}

window.addEventListener("DOMContentLoaded", addCollapse, false)
document.addEventListener("htmx:afterRequest", addCollapse, false)