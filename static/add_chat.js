function close_get_users(){
    document.getElementById("overlay2").style.display = "none"
    document.getElementById("add-chat-box").style.display = "none"
}

async function get_users(){
    user_box = document.getElementById("search-users-div")
    user_box.innerHTML = ""

    document.getElementById("add-chat-box").style.display = "block"

    document.getElementById("overlay2").style.display = "block"

    const response = await fetch('/users');
    const data = await response.json();
    for (i = 0; i < data.length; i++){
        console.log(i)
        user_div = document.createElement("div")
        user_div.setAttribute("class", "user_div")
        user_div.setAttribute("onclick", "add_direct_chat({{data[i][0]}})")

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
}