async function unread_messages(recieving_room){
    let data =  await fetch("/unread-messages-update", {
        method: "post",
        body: `{
            "recieving_room": "${recieving_room}",
            "user_id": "${user_id}"
        }`
    }).then(async (data) => {
        data = await data.json()
        return data
    })
    
    
    console.log(data)
    create_unread_message_link(recieving_room, data['amount'])
}

function create_unread_message_link(room, amount){    
    if (amount != 1){

        main_div = document.querySelector(`div[room-id='${room}']`)
        main_div.remove()
        
    }
    unread_messages_container = document.getElementById("unread-messages")
    
    main_div = document.querySelector(`a[chat_id='chat-${room}']`)
    main_div
    img = main_div.querySelector("img")
    src = img.src
    
    container = document.createElement("div")
    container.setAttribute("onclick", `location.href='/room/${room}'`)
    container.setAttribute("room-id", room)
    container.setAttribute("class", "new-message-group-div")
    img = document.createElement("img")
    img.src = src
    container.appendChild(img)

    a = document.createElement("div")
    a.setAttribute("class", "amount-unread-messages")
    a.innerHTML = amount
    container.appendChild(a)
    unread_messages_container.appendChild(container)
    
}

socket.on("change-goup-name", async function (data){
    chat = document.querySelector(`a[chat_id='chat-${data["room"]}']`)
    chat.remove()
    document.getElementById("b").insertAdjacentElement("afterend", chat)

    let room_name = await fetch("/get-group-name", {
        method: "POST",
        body: `{
            "room": "${data['room']}"
        }`
    })
    room_name = await room_name.json()
    document.querySelector(`a[chat_id="chat-${data['room']}"`).querySelector("p").innerHTML = room_name['room-name']
    
    if (data['room'] == room){
        
        //change the name for the main 
        document.querySelector("p[class='current-goup-name']").innerHTML = room_name['room-name']
    
        div = document.createElement("div")
        div.setAttribute("class", "admin-message")

        d1 = document.createElement("div")
        img = document.createElement("img")
        img.src = data['src']
        d1.appendChild(img)
        div.appendChild(d1)

        d2 = document.createElement("div")
        p = document.createElement("p")
        p.innerHTML = data['content']
        d2.appendChild(p)
        div.appendChild(d2)

        document.getElementById("massage_box").insertBefore(div, anchor)
        anchor.scrollIntoView(true)
    }

})

socket.on("leave-group",async function (data){
    chat = document.querySelector(`a[chat_id='chat-${data["room"]}']`)
    chat.remove()
    document.getElementById("b").insertAdjacentElement("afterend", chat)
    if (data['room'] == room){
        

        div = document.createElement("div")
        div.setAttribute("class", "admin-message")

        d1 = document.createElement("div")
        img = document.createElement("img")
        img.src = data['src']
        d1.appendChild(img)
        div.appendChild(d1)

        d2 = document.createElement("div")
        p = document.createElement("p")
        p.innerHTML = data['content']
        d2.appendChild(p)
        div.appendChild(d2)

        document.getElementById("massage_box").insertBefore(div, anchor)
        anchor.scrollIntoView(true)


        
        users = await fetch("/get-users-of-group", {
            method: "POST",
            body: `{
                "room": "${room}"
            }`
        })
        users = await users.json()

        user_html = ""
        for (let user of users){
            user_html += `
            <div class="chat-select" onclick="show_profile('${user[0]}')">
                <section style="position: relative;">
                    <img src="/static/profile-pic/${user[2]}">
                    <svg style="position:absolute;" width="10" height="10" >
                        <circle r="5" cx="5" cy="5" fill="#F23F43" user_id="${user[0]}" class="stat"></circle>
                    </svg>
                </section>
                
                <div>
                    <p>${user[1]}</p>
                </div>
            </div>
            
            `
        }

        document.getElementById("users-of-group").innerHTML = user_html
    }
    
})

socket.on('massage', function (data){ 
    console.log("MESSAGE!")
    chat = document.querySelector(`a[chat_id='chat-${data["room"]}']`)
    chat.remove()
    document.getElementById("b").insertAdjacentElement("afterend", chat)
    if (data['room'] != room){
        unread_messages(data['room'])
        return
        
    }
    socket.emit("set_message_seen", {"room": room, "user_id": user_id})
    let verifier = true
    if ("admin" in data){
        div = document.createElement("div")
        div.setAttribute("class", "admin-message")

        d1 = document.createElement("div")
        img = document.createElement("img")
        img.src = data['src']
        d1.appendChild(img)
        div.appendChild(d1)

        d2 = document.createElement("div")
        p = document.createElement("p")
        p.innerHTML = data['content']
        d2.appendChild(p)
        div.appendChild(d2)

        document.getElementById("massage_box").insertBefore(div, anchor)
        location.reload()
        anchor.scrollIntoView(true)
        return
    }
    else if (Array.from(document.getElementsByClassName("message")).length == 0){
        
    }
    // if last message is child checks if this message can be child -> appends itself as ""/child/parent    
    else if (Array.from(document.getElementsByClassName("message")).slice(-1)[0].hasAttribute("child")){
        let ar = Array.from(document.getElementsByClassName("message")).reverse()
        let index = 0
        
        while (index < ar.length){
            
            if (!ar[index].hasAttribute("child")){ //not child
                let text_top_old = ar[index].getElementsByClassName("text-top")[0].innerHTML.split(" ")
                let text_top_new = data['user'].split(" ")

                
                if (text_top_old[0] == text_top_new[0] &&
                    text_top_old[1] == text_top_new[1] && //create message as child
                    text_top_old[2].slice(0, 5) == text_top_new[2].slice(0, 5)){
                        
                        //ar[0].setAttribute("style", "margin-bottom: 0;")

                        let box = document.getElementById("massage_box")
    
                        let message = document.createElement('div')
                        message.setAttribute("class", "message")
                        message.setAttribute("style", "margin-bottom: 0;")
                        message.setAttribute("child", "")

                        message.appendChild(document.createElement("div"))
                        
                        console.log("img_src" in data)
                        if ("img_src" in data){ // attachment
                            console.log(data['img_src'])
                            let i = document.createElement("img")
                            i.setAttribute("style", "max-width: 300px; max-height: 300px; margin-top: 4px; margin-bottom: 4px;")
                            i.setAttribute("src", data["img_src"])
                            message.appendChild(i)

                            i.addEventListener("load", function (){
                                document.getElementById("anchor").scrollIntoView(true)
                            })
                        }
                        else{
                            let div = document.createElement("div")
                            div.setAttribute("class", "text-bottom")
                            div.setAttribute("style", "margin-top: 4px;")

                            let message_array = data['chat']
                            i = 0
                            while (i < message_array.length){
                                if ( message_array[i].includes("img--")){
                                    

                                    let img_mes = document.createElement("img")
                                    img_mes.setAttribute("src", "/static/emotes/"+message_array[i].slice(5))
                                    if (data['only_emotes']){
                                        img_mes.setAttribute("style", "max-width: 50px; max-height: 50px; display: inline-block; vertical-align: middle;")
                                    }
                                    else{
                                        img_mes.setAttribute("style", "max-width: 22px; max-height: 22px; display: inline-block; vertical-align: middle;")
                                    }
                                    div.appendChild(img_mes)
                                    img_mes.addEventListener("load", function (){
                                        document.getElementById("anchor").scrollIntoView(true)
                                    })
                                }
                                else{
                                    let p_mes = document.createElement("p")
                                    p_mes.setAttribute("style", "display: inline-block; margin-top: 0px; margin-bottom: 0px; ")
                                    p_mes.innerHTML = message_array[i]
                                    div.appendChild(p_mes)
                                }
                                i+=1
                            }
                            message.appendChild(div)
                        }
                        
                        let anchor = document.getElementById("anchor")
    
                        box.insertBefore(message, anchor);
                        verifier = false
                    }


                break
            }
        index+=1
        }
    }   //if last element s child a child
    else{
        let text_top_old = Array.from(document.getElementsByClassName("message")).slice(-1)[0].getElementsByClassName("text-top")[0].innerHTML.split(" ")
        let text_top_new = data['user'].split(" ")
        
        if (text_top_old[0] == text_top_new[0] && //create message as child
                    text_top_old[1] == text_top_new[1] &&
                    text_top_old[2].slice(0, 5) == text_top_new[2].slice(0, 5)){
                        Array.from(document.getElementsByClassName("message")).slice(-1)[0].setAttribute("style", "margin-bottom: 0;")

                        let box = document.getElementById("massage_box")
    
                        let message = document.createElement('div')
                        message.setAttribute("class", "message")
                        message.setAttribute("child", "")
                        message.setAttribute("style", "margin-bottom: 0;")

                        message.appendChild(document.createElement("div"))

                        if ("img_src" in data){ // attachment
            
                            let i = document.createElement("img")
                            i.setAttribute("style", "max-width: 300px; max-height: 300px; margin-top: 4px; margin-bottom: 4px;")
                            i.setAttribute("src", data["img_src"])
                            message.appendChild(i)

                            i.addEventListener("load", function (){
                                document.getElementById("anchor").scrollIntoView(true)
                            })
                        }
                        else{
                            let div = document.createElement("div")
                            div.setAttribute("class", "text-bottom")
                            div.setAttribute("style", "margin-top: 4px;")

                            let message_array = data['chat']
                            i = 0
                            while (i < message_array.length){
                                if ( message_array[i].includes("img--")){
                                    
                                    let img_mes = document.createElement("img")
                                    img_mes.setAttribute("src", "/static/emotes/"+message_array[i].slice(5))
                                    if (data['only_emotes']){
                                        img_mes.setAttribute("style", "max-width: 50px; max-height: 50px; display: inline-block; vertical-align: middle;")
                                    }
                                    else{
                                        img_mes.setAttribute("style", "max-width: 22px; max-height: 22px; display: inline-block; vertical-align: middle;")
                                    }
                                    div.appendChild(img_mes)
                                    img_mes.addEventListener("load", function (){
                                        document.getElementById("anchor").scrollIntoView(true)
                                    })
                                }
                                else{
                                    let p_mes = document.createElement("p")
                                    p_mes.setAttribute("style", "display: inline-block; margin-top: 0px; margin-bottom: 0px;")
                                    p_mes.innerHTML = message_array[i]
                                    div.appendChild(p_mes)
                                }
                                i+=1
                            }
                            message.appendChild(div)
                        }
                        
                        if (Array.from(document.getElementsByClassName("message")).slice(-1)[0].getElementsByClassName("text-bottom").length != 0){
                            p_elements = Array.from(Array.from(document.getElementsByClassName("message")).slice(-1)[0].getElementsByClassName("text-bottom")[0].getElementsByTagName("p")) 
                            for (i = 0; i < p_elements.length; i +=1){
                                p_elements[i].setAttribute("style", "display: inline-block; margin-top: 0px; margin-bottom: 0px;")
                            }
                        }
                        

                        let anchor = document.getElementById("anchor")

                        box.insertBefore(message, anchor);
                        verifier = false
                    }
    }
    //NORMAL ELEMENT
    if (verifier){

        
        let box = document.getElementById("massage_box")
        
        let message = document.createElement('div')
        message.setAttribute("class", "message")

        //profile pic
        let profilepicb = document.createElement("div")
        profilepicb.setAttribute("class", "emote-container")
        let profilepic = document.createElement("img")
        profilepic.setAttribute("class","profile-pic-message")
        profilepic.setAttribute("src", "/static/profile-pic/"+data['profile_pic']) //fix?
        profilepic.setAttribute("onclick", "show_profile(" + data['user_id'] + ")")
        
        profilepicb.appendChild(profilepic)
        message.appendChild(profilepicb)            
        
        //text
        let d = document.createElement("div")


        let name = document.createElement("p")
        name.innerHTML = data['user']
        name.setAttribute("class", "text-top")
        d.appendChild(name)

        if ("img_src" in data){ // attachment
            
            let i = document.createElement("img")
            i.setAttribute("style", "max-width: 300px; max-height: 300px")
            i.setAttribute("src", data["img_src"])
            d.appendChild(i)

            i.addEventListener("load", function (){
                document.getElementById("anchor").scrollIntoView(true)
            })
        }
        else{
            let text_bottom = document.createElement("div")
            text_bottom.setAttribute("class", "text-bottom")

            let mas = document.createElement('div')
            mas.setAttribute("class", "text-bottom")
            
            let message_array = data['chat']
        
            i = 0
            while (i < message_array.length){
                if ( message_array[i].includes("img--")){
                    
                    let img_mes = document.createElement("img")
                    img_mes.setAttribute("src", "/static/emotes/"+message_array[i].slice(5))

                    if (data['only_emotes']){
                        img_mes.setAttribute("style", "max-width: 50px; max-height: 50px; display: inline-block; vertical-align: middle;")
                    }
                    else{
                        img_mes.setAttribute("style", "max-width: 22px; max-height: 22px; display: inline-block; vertical-align: middle;")
                    }
                    text_bottom.appendChild(img_mes)
                    img_mes.addEventListener("load", function (){
                        document.getElementById("anchor").scrollIntoView(true)
                    })
                }
                else{
                    let p_mes = document.createElement("p")
                    p_mes.setAttribute("style", "display: inline-block; margin-top: 0px; margin-bottom: 0px;")
                    p_mes.innerHTML = message_array[i]
                    text_bottom.appendChild(p_mes)
                }
                i+=1
            }
            d.appendChild(text_bottom)
        }
        //message data
            
        message.appendChild(d)
        
        
        let anchor = document.getElementById("anchor")
        
        box.insertBefore(message, anchor);
    }
    //scroll down
    anchor.scrollIntoView(true)
})