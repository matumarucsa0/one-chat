function render_gif(){
    console.log("executing")
    input = document.getElementById("gif-search").value
    url = `https://api.giphy.com/v1/gifs/search?api_key=aCOoUMm8yoly0W6BLQySPncB363GmDD6&q=${input}&limit=5`
    fetch(url)
        .then(response => response.json())
        .then(data => {
          // Extract the GIF URLs from the response
          const gifURLs = data.data.map(gif => gif.images.fixed_height.url);

          // Render GIFs
          const gifContainer = document.getElementById('gif-container');
          gifContainer.innerHTML = ""
          gifURLs.forEach(url => {

            const img = document.createElement('img');
            img.src = url;
            img.style = "width: 231px;"
            img.setAttribute("onclick", `send_gif('${url}')`)

            gifContainer.appendChild(img);
          });
        })
        .catch(error => console.log(img));
}

function send_gif(link){
    console.log("clicked")
    socket.emit("post--",{chat: "",gif: link,username: user, user_id : user_id, profile_pic : PROFILE_PICTURE});
}
