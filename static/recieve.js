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
    img = main_div.querySelector("img")
    src = img.src
    
    container = document.createElement("div")
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

socket.on('massage', function (data){ 
    console.log("MESSAGE!")
    chat = document.querySelector(`a[chat_id='chat-${data["room"]}']`)
    chat.remove()
    document.getElementById("b").insertAdjacentElement("afterend", chat)
    if (data['room'] != room){
        unread_messages(data['room'])
        return
        
    }
    let verifier = true

    if (Array.from(document.getElementsByClassName("message")).length == 0){
        
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