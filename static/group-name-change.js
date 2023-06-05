// Wait for the page to load
window.addEventListener('DOMContentLoaded', function() {
    // Get the input field and submit button elements
    let inputField = document.querySelector("p[class='current-goup-name']");
    
    // Store the initial value of the input field
    let initialValue = inputField.innerHTML;
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
      let currentValue = inputField.innerHTML;
  
      // Compare the current value with the initial value
      if (currentValue !== initialValue) {
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
        }).then(
            location.reload()
            )
        
        // You can submit the form programmatically here if needed
        // document.getElementById('my-form').submit();
      }
    }
  });
  