function send_status(){
    socket.emit("is-online", {'user': user_id})
}

socket.on("users-online", function (data){
    users = data['users_online']
    statuses = document.getElementsByClassName("stat")
    for (i=0; i<statuses.length; i++){
        if (users.includes(String(statuses[i].getAttribute("user_id")))){
            statuses[i].setAttribute("fill", "#23a55a")
        }
        else{
            statuses[i].setAttribute("fill", "#F23F43")
        }
    }
})

var isTypingStaus;
post_content = document.getElementById("post-content") 
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

var typing_users = new Set()
var time = Date.now()
socket.on("is_typing", function (data){
    typing_users.add(data["user"])
})

function updateStatus(){
    if (time <= Date.now() - 125){
        is_typing_element = document.getElementById("is_typing_element")
        if (typing_users.size > 0){
            is_typing_p = ""
            for (userName of typing_users){
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

setInterval(isTypingEmit, 75)
setInterval(updateStatus, 100)

setInterval(send_status, 750)