document.addEventListener("DOMContentLoaded", function () {
  const chatbotContentArea = document.querySelector(".container");
  const chatbotInputField = document.querySelector("#user-input");
  const chatbotSendBtn = document.querySelector("#send-btn");
  const chatbotBox = document.querySelector(".chatbot-box");
  const chatbotCloseBtn = document.querySelector(".chatbot-close-btn");

  const scrollToBottom = () => {
    chatbotContentArea.scrollTop = chatbotContentArea.scrollHeight;
  };

  const createProfileIcon = (messageType) => {
    const profileIcon = document.createElement("a");
    profileIcon.classList.add(
      messageType === "user" ? "user-icon" : "bot-icon",
    );
    return profileIcon;
  };

  const createMessageLoader = () => {
    const loader = document.createElement("div");
    loader.classList.add("loader");
    return loader;
  };

  const addMessage = (messageType, message) => {
    const msgContainer = document.createElement("div");
    const msgElement = document.createElement("div");
    msgContainer.classList.add(`${messageType}-msg-container`);
    msgElement.classList.add(`${messageType}-msg`);
    msgElement.innerText = message;
    const profileIcon = createProfileIcon(messageType);
    if (messageType === "user") {
      msgContainer.appendChild(msgElement);
      msgContainer.appendChild(profileIcon);
    } else {
      msgContainer.appendChild(profileIcon);
      msgContainer.appendChild(msgElement);
    }
    chatbotContentArea.appendChild(msgContainer);
    scrollToBottom();
    return msgElement;
  };

  const getCookie = (name) => {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";");
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === name + "=") {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  };

  const getBotResponse = async (message) => {
    const apiUrl = document.URL.endsWith("chatbot/") ? "" : "chatbot/";
    const response = await fetch(apiUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken"),
      },
      body: JSON.stringify({ message: message }),
    });
    return await response.json();
  };

  const updateMessage = (msgElement, newMessage) => {
    msgElement.innerHTML = "";
    msgElement.innerText = newMessage;
    scrollToBottom();
  };

  const sendUserMessage = (message) => {
    const msgElement = addMessage("bot", "");
    const loader = createMessageLoader();
    msgElement.appendChild(loader);
    getBotResponse(message)
      .then((data) => {
        if (data.response) {
          updateMessage(msgElement, data.response);
        } else {
          // Handle error response
          updateMessage(msgElement, "Error: Unable to get response.");
        }
      })
      .catch((error) => {
        console.error("Error:", error);
        updateMessage(msgElement, "Error: Unable to get response.");
      });
  };

  const getMessageAndClear = () => {
    const message = chatbotInputField.value.trim();
    chatbotInputField.value = "";
    return message;
  };

  // 이벤트 리스너 추가
  chatbotSendBtn.addEventListener("click", () => {
    const message = getMessageAndClear();
    addMessage("user", message);
    sendUserMessage(message);
  });

  chatbotInputField.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      const message = getMessageAndClear();
      addMessage("user", message);
      sendUserMessage(message);
    }
  });

  chatbotCloseBtn.addEventListener("click", () => {
    if (chatbotBox.classList.contains("show")) {
      chatbotBox.classList.remove("show");
    }
  });

  scrollToBottom();

});
