socket.on('massage', function(data){ 
    console.log("MESSAGE!")
    if (data['room'] != room){
        console.log("Message in room "+ data['room'])
        return
    }
    var verifier = true

    if (Array.from(document.getElementsByClassName).length == 0){
        
    }
    // if last message is child checks if this message can be child -> appends itself as ""/child/parent    
    else if (Array.from(document.getElementsByClassName("message")).slice(-1)[0].hasAttribute("child")){
        var ar = Array.from(document.getElementsByClassName("message")).reverse()
        let index = 0
        
        while (index < ar.length){
            
            if (!ar[index].hasAttribute("child")){ //not child
                var text_top_old = ar[index].getElementsByClassName("text-top")[0].innerHTML.split(" ")
                var text_top_new = data['user'].split(" ")

                
                if (text_top_old[0] == text_top_new[0] &&
                    text_top_old[1] == text_top_new[1] && //create message as child
                    text_top_old[2].slice(0, 5) == text_top_new[2].slice(0, 5)){
                        
                        //ar[0].setAttribute("style", "margin-bottom: 0;")

                        var box = document.getElementById("massage_box")
    
                        var message = document.createElement('div')
                        message.setAttribute("class", "message")
                        message.setAttribute("style", "margin-bottom: 0;")
                        message.setAttribute("child", "")

                        message.appendChild(document.createElement("div"))
                        
                        console.log("img_src" in data)
                        if ("img_src" in data){ // attachment
                            console.log(data['img_src'])
                            var i = document.createElement("img")
                            i.setAttribute("style", "max-width: 300px; max-height: 300px; margin-top: 4px; margin-bottom: 4px;")
                            i.setAttribute("src", data["img_src"])
                            message.appendChild(i)

                            i.addEventListener("load", function (){
                                document.getElementById("anchor").scrollIntoView(true)
                            })
                        }
                        else{
                            var div = document.createElement("div")
                            div.setAttribute("class", "text-bottom")
                            div.setAttribute("style", "margin-top: 4px;")

                            var message_array = data['chat']
                            i = 0
                            while (i < message_array.length){
                                if ( message_array[i].includes("img--")){
                                    

                                    var img_mes = document.createElement("img")
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
                                    var p_mes = document.createElement("p")
                                    p_mes.setAttribute("style", "display: inline-block; margin-top: 0px; margin-bottom: 0px; ")
                                    p_mes.innerHTML = message_array[i]
                                    div.appendChild(p_mes)
                                }
                                i+=1
                            }
                            message.appendChild(div)
                        }
                        
                        var anchor = document.getElementById("anchor")
    
                        box.insertBefore(message, anchor);
                        verifier = false
                    }


                break
            }
        index+=1
        }
    }   //if last element s child a child
    else{
        var text_top_old = Array.from(document.getElementsByClassName("message")).slice(-1)[0].getElementsByClassName("text-top")[0].innerHTML.split(" ")
        var text_top_new = data['user'].split(" ")
        
        if (text_top_old[0] == text_top_new[0] && //create message as child
                    text_top_old[1] == text_top_new[1] &&
                    text_top_old[2].slice(0, 5) == text_top_new[2].slice(0, 5)){
                        Array.from(document.getElementsByClassName("message")).slice(-1)[0].setAttribute("style", "margin-bottom: 0;")

                        var box = document.getElementById("massage_box")
    
                        var message = document.createElement('div')
                        message.setAttribute("class", "message")
                        message.setAttribute("child", "")
                        message.setAttribute("style", "margin-bottom: 0;")

                        message.appendChild(document.createElement("div"))

                        if ("img_src" in data){ // attachment
            
                            var i = document.createElement("img")
                            i.setAttribute("style", "max-width: 300px; max-height: 300px; margin-top: 4px; margin-bottom: 4px;")
                            i.setAttribute("src", data["img_src"])
                            message.appendChild(i)

                            i.addEventListener("load", function (){
                                document.getElementById("anchor").scrollIntoView(true)
                            })
                        }
                        else{
                            var div = document.createElement("div")
                            div.setAttribute("class", "text-bottom")
                            div.setAttribute("style", "margin-top: 4px;")

                            var message_array = data['chat']
                            i = 0
                            while (i < message_array.length){
                                if ( message_array[i].includes("img--")){
                                    
                                    var img_mes = document.createElement("img")
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
                                    var p_mes = document.createElement("p")
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
                        

                        var anchor = document.getElementById("anchor")

                        box.insertBefore(message, anchor);
                        verifier = false
                    }
    }
    //NORMAL ELEMENT
    if (verifier){

        
        var box = document.getElementById("massage_box")
        
        var message = document.createElement('div')
        message.setAttribute("class", "message")

        //profile pic
        var profilepicb = document.createElement("div")
        profilepicb.setAttribute("class", "emote-container")
        var profilepic = document.createElement("img")
        profilepic.setAttribute("class","profile-pic-message")
        profilepic.setAttribute("src", "/static/profile-pic/"+data['profile_pic']) //fix?
        profilepic.setAttribute("onclick", "show_profile(" + data['user_id'] + ")")
        
        profilepicb.appendChild(profilepic)
        message.appendChild(profilepicb)            
        
        //text
        var d = document.createElement("div")


        var name = document.createElement("p")
        name.innerHTML = data['user']
        name.setAttribute("class", "text-top")
        d.appendChild(name)

        if ("img_src" in data){ // attachment
            
            var i = document.createElement("img")
            i.setAttribute("style", "max-width: 300px; max-height: 300px")
            i.setAttribute("src", data["img_src"])
            d.appendChild(i)

            i.addEventListener("load", function (){
                document.getElementById("anchor").scrollIntoView(true)
            })
        }
        else{
            var text_bottom = document.createElement("div")
            text_bottom.setAttribute("class", "text-bottom")

            var mas = document.createElement('div')
            mas.setAttribute("class", "text-bottom")
            
            var message_array = data['chat']
        
            i = 0
            while (i < message_array.length){
                if ( message_array[i].includes("img--")){
                    
                    var img_mes = document.createElement("img")
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
                    var p_mes = document.createElement("p")
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
        
        
        var anchor = document.getElementById("anchor")
        
        box.insertBefore(message, anchor);
    }
    //scroll down
    anchor.scrollIntoView(true)
})