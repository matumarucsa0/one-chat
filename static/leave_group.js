async function leave_group(user, method, room, removing_user=""){
    await fetch("/leave-group", {
        method: "post",
        body: `{
            "user": "${user}",
            "method": "${method}",
            "room": "${room}",
            "removing-user": "${removing_user}"
        }`
    }).then(location.reload())
}