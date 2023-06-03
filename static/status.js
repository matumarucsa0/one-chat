function send_status(){
    socket.emit("is-online", {'user': user_id})
}

socket.on("users-online", function (data){
    let users = data['users_online']
    let statuses = document.getElementsByClassName("stat")
    for (const user_stauts of statuses){
        if (users.includes(String(user_stauts.getAttribute("user_id")))){
            user_stauts.setAttribute("fill", "#23a55a")
        }
        else{
            user_stauts.setAttribute("fill", "#F23F43")
        }
    }
})

let isTypingStaus;
let post_content = document.getElementById("post-content") 
post_content.addEventListener("input", function (){
    if (post_content.innerHTML != ""){
        isTypingStaus = true
    }
    else{
        isTypingStaus = false
    }
})

function isTypingEmit(){
    if (isTypingStaus){
        socket.emit("typing", {"user": user, "user_id": user_id, "room": room})
    }
}

let typing_users = new Set()
let time = Date.now()
socket.on("is_typing", function (data){
    if (data['room'] == room && data['user_id'] != user_id){
        typing_users.add(data["user"])
    }
})

function updateStatus(){
    if (time <= Date.now() - 200){
        
        let typing_users_array = Array.from(typing_users)
        typing_users_array = typing_users_array.sort()
        let is_typing_element = document.getElementById("is_typing_element")
        if (typing_users_array.length > 0){
            let is_typing_p = ""
            for (let userName of typing_users_array){
                is_typing_p += `${userName} is typing..., `            
            }
            is_typing_element.style.display = "block"
            is_typing_element.innerHTML = is_typing_p
            typing_users = new Set()    
        }
        else{
            is_typing_element.style.display = "none"
        }
    }
}

setInterval(isTypingEmit, 90)
setInterval(updateStatus, 190)

setInterval(send_status, 750)