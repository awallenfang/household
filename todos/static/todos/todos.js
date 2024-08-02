function toggleDropdown(e) {
    console.log(e)
    let dropdown = e.target.parentElement.parentElement.nextElementSibling

    if (dropdown.classList.contains("dropdown-open")) {
        dropdown.classList.remove("dropdown-open")
        dropdown.classList.add("dropdown-closed")
    } else {
        dropdown.classList.remove("dropdown-closed")
        dropdown.classList.add("dropdown-open")

    }
}

function drop(ev) {
    ev.preventDefault()

    let left = ev.target.getAttribute("left")
    let right = ev.target.getAttribute("right")
    let status = ev.target.getAttribute("todo-status")
    let id = ev.dataTransfer.getData('todo-id')
    let url = `/todos/${id}/${left}/${right}/${status}/reorder`
    console.log(url)
    htmx.ajax("POST", url, {target:'#todo-list', swap:'outerHTML'})
}

function allowDrop(ev) {
    ev.preventDefault()
}

function setupDragEnv(e) {
    let handles = document.getElementsByClassName("todo_drag_handle")
    let drop_spots = document.getElementsByClassName("todo-drop-spot")
    console.log(drop_spots)
    console.log("wsf")
    console.log(handles)

    for (let handle of handles) {
        let draggable_elem = handle.closest('.draggable-container')

        handle.onmousedown = function(e) {
            draggable_elem.setAttribute('draggable', 'true');
            console.log("Dragstart")
            
        }
        handle.onmouseup = function(e) {
            draggable_elem.setAttribute('draggable', 'false');
            
        }
        draggable_elem.ondragstart = function(e) {
            let todo_id = e.target.getAttribute("todo-id")
            e.dataTransfer.setData('todo-id', todo_id)
            e.dataTransfer.setData('text/plain', 'handle');
            for (let drop_spot of drop_spots) {
                console.log("B")
                drop_spot.style.display = "block"
            }
        }
        draggable_elem.ondragend = function(e) {
            e.target.setAttribute('draggable', 'false')
            for (let drop_spot of drop_spots) {
                console.log("A")
                drop_spot.style.display = "none"
            }
      };
    }
}

document.addEventListener("DOMContentLoaded", function(e) {
    setupDragEnv(e)
})

document.addEventListener('htmx:afterSwap', function(e) {
    setupDragEnv(e)
});