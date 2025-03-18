let socket = new WebSocket("ws://localhost:8000/ws");

socket.onmessage = function(event) {
    let emails = JSON.parse(event.data);
    let emailList = document.getElementById("emailList");
    emailList.innerHTML = "";
    emails.forEach(email => {
        let li = document.createElement("li");
        li.innerHTML = `<b>${email.subject}</b> from ${email.sender}: ${email.body}`;
        emailList.appendChild(li);
    });
};

async function generateEmail() {
    let response = await fetch("http://localhost:8000/generate_email", { method: "POST" });
    let data = await response.json();
    document.getElementById("email").innerText = data.email;
}
