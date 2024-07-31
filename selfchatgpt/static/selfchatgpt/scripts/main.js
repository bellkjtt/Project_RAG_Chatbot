const header = document.querySelector("header");
const logoImg = document.querySelector(".logo-img");
const HeaderItems = document.querySelectorAll(".header-item");
const chatbotBox = document.querySelector(".chatbot-box");
const chatbotBtn = document.querySelector(".chatbot-btn");
const chatbotContentArea = document.querySelector(".container");
const mainPage = document.querySelector("#main");

const scrollToBottom = () => {
  chatbotContentArea.scrollTop = chatbotContentArea.scrollHeight;
};

chatbotBtn.addEventListener("click", () => {
  if (chatbotBox.classList.contains("show")) {
    chatbotBox.classList.remove("show");
  } else {
    chatbotBox.classList.add("show");
    scrollToBottom();
  }
});

chatbotBtn.addEventListener("dblclick", (e) => {
  e.preventDefault();
  e.stopPropagation();
});

chatbotBtn.addEventListener("mousedown", (e) => {
  e.preventDefault();
  e.stopPropagation();
});

HeaderItems.forEach((element) => {
  element.addEventListener("mouseenter", () => {
    header.classList.add("transparent");
    logoImg.classList.add("dark");
    if (element.classList.contains("focus-chatbot-btn")) {
      const panel = document.querySelector(".panel");
      panel.classList.add("dimmer");
      const chatbotHelper = document.createElement("p");
      chatbotHelper.classList.add("chatbot-helper");
      chatbotHelper.innerText = "챗봇 버튼을 클릭해서 사용할 수도 있습니다. →";
      mainPage.after(chatbotHelper);
    }
    HeaderItems.forEach((sibling) => {
      if (sibling !== element) {
        sibling.classList.add("dimmed");
      }
    });
  });
  element.addEventListener("mouseleave", () => {
    header.classList.remove("transparent");
    logoImg.classList.remove("dark");
    if (element.classList.contains("focus-chatbot-btn")) {
      const panel = document.querySelector(".panel");
      panel.classList.remove("dimmer");
      const chatbotHelper = document.querySelector(".chatbot-helper");
      chatbotHelper.remove();
    }
    HeaderItems.forEach((sibling) => {
      sibling.classList.remove("dimmed");
    });
  });
    
});
