function close_get_users(){
    document.getElementById("overlay2").style.display = "none"
    document.getElementById("add-chat-box").style.display = "none"
    document.getElementsByClassName("add-chat-bottom")[0].style = ""
}

async function get_users_direct(){
    user_box = document.getElementById("search-users-div")
    user_box.innerHTML = ""

    document.getElementById("add-chat-box").style.display = "block"

    document.getElementById("overlay2").style.display = "block"


    const response = await fetch('/users');
    const data = await response.json();
    for (i = 0; i < data.length; i++){

        user_div = document.createElement("div")
        user_div.setAttribute("class", "user_div")
        user_div.setAttribute("onclick", `add_direct_chat(${data[i][0]})`)

        img = document.createElement("img")
        img.setAttribute("src", `/static/profile-pic/${data[i][2]}`)
        user_div.appendChild(img)

        name_ = document.createElement("p")
        name_.innerHTML = data[i][1]
        user_div.appendChild(name_)

        user_box.appendChild(user_div)
    }
}

async function add_direct_chat(id){
    response = await fetch("/add-chat", {
    method: "POST",
    body: `{
        "id": "${id}"
    }`
   });
   status_ = await response.json()
   console.log(status_)
   console.log(response)
   if ('error' == status_['status']){
    alert("The chat already exists")
   }
   else{
    location.reload()
   }
   
}

async function get_users_group(){
    user_box = document.getElementById("search-users-div")
    user_box.innerHTML = ""

    document.getElementById("add-chat-box").style.display = "block"
    document.getElementsByClassName("add-chat-bottom")[0].style = ` height: 196px;
                                                                    box-sizing: border-box;
                                                                    overflow-y: scroll;
                                                                    padding: 0px 25px 0px 25px; `
    
    document.getElementById("overlay2").style.display = "block"

    const response = await fetch('/users');
    const data = await response.json();
    for (i = 0; i < data.length; i++){

        user_div = document.createElement("div")
        user_div.setAttribute("class", "user_div")
        user_div.setAttribute("onclick", `select_checkbox('checkbox-${i}')`)

        img = document.createElement("img")
        img.setAttribute("src", `/static/profile-pic/${data[i][2]}`)
        user_div.appendChild(img)

        name_ = document.createElement("p")
        name_.innerHTML = data[i][1]
        user_div.appendChild(name_)

        checkbox = document.createElement("input")
        checkbox.setAttribute("type", "checkbox")
        checkbox.setAttribute("class", "checkbox")
        checkbox.setAttribute("id", `checkbox-${i}`)
        checkbox.setAttribute("user_id", data[i][0])
        user_div.appendChild(checkbox)
        
        user_div.appendChild(document.createElement("div"))

        user_box.appendChild(user_div)
    }
    main_box = document.getElementById("add-chat-box")

    abs_bottom = document.createElement("div")
    abs_bottom.setAttribute("class", "abs_bottom")

    abs_bottom_button = document.createElement("button")
    abs_bottom_button.innerHTML = "Create Group"
    abs_bottom_button.setAttribute("onclick", "add_group()")

    abs_bottom.appendChild(abs_bottom_button)

    main_box.appendChild(abs_bottom)

}

function select_checkbox(checkbox_id){
    document.getElementById(checkbox_id).checked = !document.getElementById(checkbox_id).checked
}

async function add_group(){
    options = document.getElementsByClassName("checkbox")
    console.log(options)
    users_to_the_goup = []
    for (i = 0; i < options.length; i++){
        console.log(options[i].checked)
        console.log(options[i].getAttribute('user_id'))
        if (options[i].checked){
            users_to_the_goup.push(options[i].getAttribute('user_id')) 
        }
    }
    console.log(users_to_the_goup)
    response = await fetch("/add-group", {
        method: "POST",
        body: `{
            "user_id_array": "${users_to_the_goup}"
        }`
       });
    
   location.reload()
}