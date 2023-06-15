// Wait for the page to load
window.addEventListener('DOMContentLoaded', function() {
    // Get the input field and submit button elements
    let inputField = document.querySelector("p[class='current-goup-name']");
    
    // Store the initial value of the input field
    let initialValue = remove_html_space(inputField.innerHTML).trim();
    console.log(initialValue)
    // Add event listener for when the input field is blurred
    inputField.addEventListener('keydown', function(e) {
        if (e.keyCode == 13){
            inputField.blur()
            console.log("enter")
        }
    });

    inputField.addEventListener('blur', function() {
        checkChanges();
      });
  
    async function checkChanges() {
      let currentValue = remove_html_space(inputField.innerHTML).trim();
  
      // Compare the current value with the initial value
      if (currentValue != initialValue) {
        // Display the changes in the output div

        console.log(initialValue + ' => ' + currentValue)
        await fetch("/change-group-name", {
            "method": "POST",
            "body": `{
                "room": ${room},
                "originalName": "${initialValue}",
                "newName": "${currentValue}",
                "user_id": "${user_id}",
                "username": "${user}"
            }`
        })
        initialValue = currentValue;
        // You can submit the form programmatically here if needed
        // document.getElementById('my-form').submit();
      }
    else{
      inputField.innerHTML = initialValue;
    }
    }
  });
  

function remove_html_space(string){
  while (string.includes("&nsbp;")){
    string = string.replace("&nsbp;")
  }
  return string
}

const divisor = document.getElementById("the-divisor")
content = document.getElementById("users-of-group")
const content_inner =  content.innerHTML
const message_content = document.getElementById("post-content")
function side_users(){

  if (divisor.classList.contains("main-div-group")){
    message_content.setAttribute("style", "width: calc(100vw - 460px)") 

    document.getElementById("users-of-group").remove()
    divisor.setAttribute("class", "")
  }
  else{
    message_content.setAttribute("style", "width: calc(100vw - 692px)")

    divisor.innerHTML += `<div id="users-of-group">${content_inner}</div>`
    divisor.setAttribute("class", "main-div-group")
  }
}