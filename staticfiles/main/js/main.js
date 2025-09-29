console.log("JavaScript подключен к Django!");

document.addEventListener('DOMContentLoaded', function() {
  const header = document.querySelector('.header');
  const headerLower = document.querySelector('.header__lower');
  let lastScrollTop = 0;
  let scrollTimer;
  
  // Добавляем класс для скрытия меню при скролле вниз
  window.addEventListener('scroll', function() {
      clearTimeout(scrollTimer);
      
      const currentScrollTop = window.pageYOffset || document.documentElement.scrollTop;
      
      // Проверяем направление скролла
      if (currentScrollTop > lastScrollTop && currentScrollTop > 50) {
          // Прокрутка вниз - скрываем меню
          header.classList.add('header--menu-hidden');
      } else {
          // Прокрутка вверх - показываем меню
          header.classList.remove('header--menu-hidden');
      }
      
      lastScrollTop = currentScrollTop;
      
      // Устанавливаем таймер для скрытия меню после остановки скролла
      scrollTimer = setTimeout(function() {
          if (currentScrollTop > 50) {
              header.classList.add('header--menu-hidden');
          }
      }, 1500); // Скрываем через 1.5 секунды после остановки скролла
  });
  
  // Показываем нижнюю часть header при наведении
  header.addEventListener('mouseenter', function() {
      header.classList.remove('header--menu-hidden');
  });
  
  // Скрываем нижнюю часть при уходе курсора, если страница проскроллена
  header.addEventListener('mouseleave', function() {
      const currentScrollTop = window.pageYOffset || document.documentElement.scrollTop;
      if (currentScrollTop > 50) {
          header.classList.add('header--menu-hidden');
      }
  });
});




// Функция для получения CSRF-токена из cookies
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + "=")) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

const csrftoken = getCookie("csrftoken");

// =============================
// Работа со статическими элементами
// =============================
document.addEventListener("scroll", function () {
  const ceoElement = document.getElementById("form_contact");
  const contactForm = document.querySelector(".form__contact");
  if (!ceoElement || !contactForm) return;
  const ceoPosition = ceoElement.getBoundingClientRect();
  if (ceoPosition.top <= window.innerHeight) {
    contactForm.style.opacity = "1";
    contactForm.style.transform = "translateY(0)";
  } else {
    contactForm.style.opacity = "0";
    contactForm.style.transform = "translateY(100%)";
  }
});

// =============================
// Slideshow (с использованием jQuery и GSAP)
// =============================
class Slideshow {
  constructor(userOptions = {}) {
    const defaultOptions = {
      $el: $(".slideshow"),
      showArrows: false,
      showPagination: true,
      duration: 10000,
      autoplay: true
    };
    
    const options = Object.assign({}, defaultOptions, userOptions);
    this.$el = options.$el;
    this.maxSlide = this.$el.find($('.js-slider-home-slide')).length;
    this.showArrows = this.maxSlide > 1 ? options.showArrows : false;
    this.showPagination = options.showPagination;
    this.currentSlide = 1;
    this.isAnimating = false;
    this.animationDuration = 1200;
    this.autoplaySpeed = options.duration;
    this.interval = null;
    this.$controls = this.$el.find('.js-slider-home-button');
    this.autoplay = this.maxSlide > 1 ? options.autoplay : false;
    
    this.$el.on("click", ".js-slider-home-next", () => this.nextSlide());
    this.$el.on("click", ".js-slider-home-prev", () => this.prevSlide());
    this.$el.on("click", ".js-pagination-item", event => {
      if (!this.isAnimating) {
        this.preventClick();
        this.goToSlide(event.target.dataset.slide);
      }
    });
    
    this.init();
  }
  
  init() {
    this.goToSlide(1);
    if (this.autoplay) this.startAutoplay();
    if (this.showPagination) {
      let pagination = '<div class="pagination"><div class="container">';
      for (let i = 1; i <= this.maxSlide; i++) {
        pagination += `<span class="pagination__item js-pagination-item ${i === 1 ? "is-current" : ""}" data-slide="${i}">${i}</span>`;
      }
      pagination += '</div></div>';
      this.$el.append(pagination);
    }
  }
  
  preventClick() {
    this.isAnimating = true;
    this.$controls.prop("disabled", true);
    clearInterval(this.interval);
    setTimeout(() => {
      this.isAnimating = false;
      this.$controls.prop("disabled", false);
      if (this.autoplay) this.startAutoplay();
    }, this.animationDuration);
  }
  
  goToSlide(index) {
    this.currentSlide = parseInt(index, 10);
    if (this.currentSlide > this.maxSlide) this.currentSlide = 1;
    if (this.currentSlide === 0) this.currentSlide = this.maxSlide;
    
    const $slides = this.$el.find(".js-slider-home-slide");
    const newCurrent = $slides.filter(`[data-slide="${this.currentSlide}"]`);
    const newPrev = this.currentSlide === 1 ? $slides.last() : newCurrent.prev(".js-slider-home-slide");
    const newNext = this.currentSlide === this.maxSlide ? $slides.first() : newCurrent.next(".js-slider-home-slide");
    
    $slides.removeClass("is-prev is-next is-current");
    this.$el.find(".js-pagination-item").removeClass("is-current");
    
    if (this.maxSlide > 1) {
      newPrev.addClass("is-prev");
      newNext.addClass("is-next");
    }
    newCurrent.addClass("is-current");
    this.$el.find(`.js-pagination-item[data-slide="${this.currentSlide}"]`).addClass("is-current");
  }
  
  nextSlide() {
    this.preventClick();
    this.goToSlide(this.currentSlide + 1);
  }
  
  prevSlide() {
    this.preventClick();
    this.goToSlide(this.currentSlide - 1);
  }
  
  startAutoplay() {
    this.interval = setInterval(() => {
      if (!this.isAnimating) this.nextSlide();
    }, this.autoplaySpeed);
  }
  
  destroy() {
    this.$el.off();
  }
}

(function () {
  let loaded = false;
  const maxLoad = 3000;  
  function load() {
    const options = { showPagination: true };
    new Slideshow(options);
  }
  
  function addLoadClass() {
    $("body").addClass("is-loaded");
    setTimeout(() => $("body").addClass("is-animated"), 600);
  }
  
  $(window).on("load", () => {
    if (!loaded) {
      loaded = true;
      load();
    }
  });
  
  setTimeout(() => {
    if (!loaded) {
      loaded = true;
      load();
    }
  }, maxLoad);
  
  addLoadClass();
})();

// =============================
// Навигация нижнего меню (fade-эффект)
// =============================
$(document).ready(function () {
  $(".header__lower-link").click(function (e) {
    e.preventDefault();
    const targetHref = e.currentTarget.getAttribute("href");
    $("#fadeScreen").css({ opacity: "0.8", "pointer-events": "auto" });
    setTimeout(() => (window.location.href = targetHref), 400);
    setTimeout(() => $("#fadeScreen").css({ opacity: "0", "pointer-events": "none" }), 500);
  });
});

// =============================
// Функция плавного скролла к элементу
// =============================
function scrollToElement(elementId) {
  const element = document.getElementById(elementId);
  if (element) {
    element.scrollIntoView({ behavior: "smooth", block: "start" });
  }
}

// =============================
// Инициализация Swiper
// =============================
const swiper = new Swiper(".swiper", {
  direction: "horizontal",
  loop: true,
  parallax: true,
  a11y: {
    prevSlideMessage: "Previous slide",
    nextSlideMessage: "Next slide",
  },
  autoplay: { delay: 5000 },
  effect: "fade",
  fadeEffect: { crossFade: true },
  pagination: { el: ".swiper-pagination", clickable: true },
});

const newSwiper = new Swiper(".swiper-container", {
  autoplay: false,
  pagination: { el: ".swiper-pagination", clickable: true },
  mousewheel: true,
  breakpoints: {
    320: { slidesPerView: 1, spaceBetween: 20 },
    680: { slidesPerView: 4, spaceBetween: 30 },
    1240: { slidesPerView: 5, spaceBetween: 40 },
  }
});

// =============================
// FAQ Toggle
// =============================
document.querySelectorAll(".faq__item-button").forEach((el) => {
  el.addEventListener("click", () => {
    const faqInfo = el.closest(".faq__item").querySelector(".faq__item-info");
    faqInfo.classList.toggle("ac-active");
  });
});

// Services Tabs & Animation - Облегченная версия
document.addEventListener('DOMContentLoaded', () => {
  // Получаем элементы
  const serviceItems = document.querySelectorAll('.services__item');
  const containerBlocks = document.querySelectorAll('.services__container-block');
  const desktopBlocks = document.querySelectorAll('.services__desktop-block');
  
  // Принудительно добавляем класс appear ко всем блокам для гарантии их отображения
  desktopBlocks.forEach(block => {
    setTimeout(() => {
      block.classList.add('appear');
    }, 100);
  });
  
  document.querySelectorAll('.services__item').forEach(item => {
    setTimeout(() => {
      item.classList.add('appear');
    }, 100);
  });
  
  // Облегченная анимация содержимого
  const animateContent = (index) => {
    const currentBlock = containerBlocks[index];
    if (!currentBlock) return;
    
    // Добавляем класс для анимации
    currentBlock.classList.add('animate-content');
    
    // Добавляем стили для анимации
    if (!document.getElementById('content-animation-styles')) {
      const style = document.createElement('style');
      style.id = 'content-animation-styles';
      style.textContent = `
        .animate-content {
          animation: fadeSlideUp 0.5s ease-out forwards;
        }
        
        .animate-content .services__container-title {
          animation: fadeSlideUp 0.5s ease-out forwards;
        }
        
        .animate-content .services__container-discr p,
        .animate-content .services__container-discr li {
          opacity: 0;
          animation: fadeSlideUp 0.5s ease-out forwards;
        }
        
        .animate-content .services__container-discr p:nth-child(2) {
          animation-delay: 0.1s;
        }
        
        .animate-content .services__container-discr p:nth-child(3) {
          animation-delay: 0.15s;
        }
        
        .animate-content .services__container-discr p:nth-child(n+4) {
          animation-delay: 0.2s;
        }
        
        .animate-content .services__container-img {
          opacity: 0;
          animation: fadeIn 0.7s ease-out 0.2s forwards;
        }
        
        @keyframes fadeSlideUp {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        
        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }
      `;
      document.head.appendChild(style);
    }
  };
  
  // Функция для переключения табов
  const switchTab = (index) => {
    // Удаляем активные классы
    serviceItems.forEach(item => {
      item.classList.remove('services__item--active');
    });
    
    containerBlocks.forEach(block => {
      block.classList.remove('services__container-block--active');
    });
    
    // Добавляем активный класс к выбранному элементу
    if (serviceItems[index]) {
      serviceItems[index].classList.add('services__item--active');
    }
    
    if (containerBlocks[index]) {
      containerBlocks[index].classList.add('services__container-block--active');
      // Запускаем анимацию
      animateContent(index);
    }
  };
  
  // Добавляем обработчики событий для табов
  serviceItems.forEach((item, index) => {
    item.addEventListener('click', () => switchTab(index));
  });
  
  // Обработчики для десктопных блоков с кнопками
  document.querySelectorAll('.services__decktop-button').forEach((button, index) => {
    button.addEventListener('click', (e) => {
      e.stopPropagation();
      // Создать модальное окно или выполнить другую логику по клику на кнопку
      console.log(`Выбрана услуга: ${index + 1}`);
    });
  });
  
  // Функция для корректного склонения слова "проект"
  const getProjectWord = (count) => {
    const words = ['проект', 'проекта', 'проектов'];
    let mod = count % 100;
    
    if (mod > 10 && mod < 20) {
      return words[2];
    }
    
    mod = count % 10;
    if (mod === 1) {
      return words[0];
    } else if (mod >= 2 && mod <= 4) {
      return words[1];
    } else {
      return words[2];
    }
  };
  
  // Обновляем счетчик проектов
  setTimeout(() => {
    document.querySelectorAll('.services__desktop-discr[data-max-projects]').forEach(el => {
      if (!el.dataset.maxProjects) return;
      
      const maxProjects = parseInt(el.dataset.maxProjects);
      const availableProjects = maxProjects - 1; // Предполагаем, что один проект уже занят
      
      if (availableProjects <= 0) {
        el.textContent = 'В этом месяце больше не принимаем проекты';
        el.style.color = '#d63031';
      } else {
        const projectWord = getProjectWord(availableProjects);
        el.textContent = `Можем взять еще ${availableProjects} ${projectWord} в этом месяце`;
      }
    });
  }, 300);
  
  // Инициализируем первый таб
  if (serviceItems.length > 0) {
    setTimeout(() => {
      switchTab(0); 
    }, 300);
  }
});

// =============================
// Chatbot Functionality
// =============================
document.addEventListener("DOMContentLoaded", () => {
  // Проверяем, не инициализирован ли уже чат
  if (window.chatbotInitialized) {
    return;
  }
  
  const chatbotContainer = document.getElementById("chatbot-container");
  const chatbotToggle = document.getElementById("chatbot-toggle");
  const chatbotClose = document.getElementById("chatbot-close");
  const chatbotInput = document.getElementById("chatbot-input");
  const chatbotSend = document.getElementById("chatbot-send");
  const chatbotMessages = document.querySelector(".chatbot-messages");
  const notification = document.getElementById("chat-notification");
  
  if (!chatbotToggle || !chatbotClose || !chatbotInput || !chatbotSend || !chatbotMessages || !notification) {
    // Не показываем ошибку, если элементы отсутствуют (могут быть в другом файле)
    return;
  }
  
  // Отмечаем, что чат инициализирован
  window.chatbotInitialized = true;
  
  let sessionId = null;
  const welcomeMessage = "Привет! Чем можем помочь?";
  
  function addMessageWithTypewriter(text, sender) {
    const messageElement = document.createElement("div");
    messageElement.className = `message ${sender}`;
    messageElement.style.cssText = "padding: 8px; margin: 5px 0; border-radius: 5px; max-width: 80%; word-wrap: break-word;";
    chatbotMessages.appendChild(messageElement);
    let index = 0;
    const delay = 30;
    const interval = setInterval(() => {
      messageElement.innerHTML = text.substring(0, index).replace(/\n/g, "<br>");
      index++;
      if (index > text.length) clearInterval(interval);
      chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
    }, delay);
  }
  
  function addMessage(text, sender) {
    const messageElement = document.createElement("div");
    messageElement.className = `message ${sender}`;
    messageElement.innerHTML = text;
    chatbotMessages.appendChild(messageElement);
    chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
  }
  
  function sendMessage() {
    const message = chatbotInput.value.trim();
    if (!message) return;
    addMessage(message, "user");
    chatbotInput.value = "";
    const requestData = sessionId ? { message, session_id: sessionId } : { message };
  
    fetch("https://api.expert-ai.ru/api/chat/expertsmet", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(requestData)
    })
      .then(response => {
        if (!response.ok) {
          throw new Error(`Ошибка сервера: ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        if (!sessionId && data.session_id) sessionId = data.session_id;
        if (data.reply) {
          addMessageWithTypewriter(data.reply, "bot");
        } else {
          addMessage("Не удалось получить ответ от AI", "bot");
        }
      })
      .catch(error => {
        console.error("Ошибка запроса:", error);
        addMessage("Произошла ошибка при отправке запроса", "bot");
      });
  }
  
  function openChat() {
    if (chatbotContainer.style.display === "none" || chatbotContainer.style.display === "") {
      chatbotContainer.style.display = "flex";
    }
    notification.style.display = "none";
    chatbotToggle.style.display = "none";
    if (chatbotMessages.childElementCount === 0) {
      addMessageWithTypewriter(welcomeMessage, "bot");
    }
  }
  
  chatbotToggle.addEventListener("click", openChat);
  chatbotClose.addEventListener("click", () => {
    chatbotContainer.style.display = "none";
    chatbotToggle.style.display = "block";
  });
  notification.addEventListener("click", openChat);
  setTimeout(() => { notification.style.display = "block"; }, 15000);
  chatbotSend.addEventListener("click", sendMessage);
  chatbotInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      sendMessage();
    }
  });
});

// =============================
// Quiz Functionality
// =============================
let quizAnswers = {};
let currentQuestion = 1;
const totalQuestions = 5;

document.addEventListener("DOMContentLoaded", () => {
  showQuestion(currentQuestion);
  updateProgressBar();
  
  document.querySelectorAll(".question__input").forEach(block => {
    block.addEventListener("click", () => {
      const radio = block.querySelector('input[type="radio"]');
      if (radio) {
        radio.checked = true;
        const question = block.closest(".question");
        question.querySelectorAll(".question__input").forEach(el => el.classList.remove("selected"));
        block.classList.add("selected");
        quizAnswers[radio.name] = radio.value;
      }
    });
  });
  
  document.querySelectorAll('.question__input input[type="radio"]').forEach(input => {
    input.addEventListener("change", () => {
      quizAnswers[input.name] = input.value;
    });
  });
  
  const contactForm = document.querySelector(".questions__contact-container");
  if (contactForm) {
    contactForm.addEventListener("submit", e => {
      e.preventDefault();
      contactForm.querySelectorAll("input[type='hidden']").forEach(el => el.remove());
      Object.keys(quizAnswers).forEach(key => {
        const hiddenInput = document.createElement("input");
        hiddenInput.type = "hidden";
        hiddenInput.name = key;
        hiddenInput.value = quizAnswers[key];
        contactForm.appendChild(hiddenInput);
      });
      const formData = new FormData(contactForm);
      fetch("/send-form/", {
        method: "POST",
        credentials: "same-origin",
        headers: {
          "X-CSRFToken": getCookie("csrftoken")
        },
        body: formData,
      })
        .then(response => {
          if (!response.ok) {
            throw new Error(`Ошибка сервера: ${response.status}`);
          }
          return response.text();
        })
        .then(data => {
          console.log(data);
          alert("Спасибо, ваш запрос отправлен!");
          if (typeof closeForm === "function") closeForm();
        })
        .catch(error => console.error("Ошибка:", error));
    });
  }
});

function showQuestion(questionNumber) {
  document.querySelectorAll(".question").forEach(q => q.style.display = "none");
  if (questionNumber <= totalQuestions) {
    document.getElementById(`question${questionNumber}`).style.display = "block";
  } else {
    document.getElementById("contactForm").style.display = "block";
  }
  updateProgressBar();
}

function nextQuestion() {
  if (isAnswerSelected(currentQuestion)) {
    currentQuestion++;
    showQuestion(currentQuestion);
  } else {
    alert("Пожалуйста, выберите ответ, чтобы продолжить.");
  }
}

function isAnswerSelected(questionNumber) {
  const inputs = document.querySelectorAll(`#question${questionNumber} input[type="radio"]`);
  return Array.from(inputs).some(input => input.checked);
}

function updateProgressBar() {
  const progress = Math.min((currentQuestion / totalQuestions) * 100, 100);
  const progressBar = document.getElementById("progressBar");
  const progressPercentage = document.getElementById("progressPercentage");
  if (progressBar && progressPercentage) {
    progressBar.style.width = `${progress}%`;
    progressPercentage.textContent = `${Math.round(progress)}%`;
  }
}

function submitQuiz() {
  const userName = document.getElementById("userName").value.trim();
  const userPhone = document.getElementById("userPhone").value.trim();
  
  if (!userName) {
    alert("Пожалуйста, введите ваше имя.");
    return;
  }
  const phonePattern = /^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$/im;
  if (!phonePattern.test(userPhone)) {
    alert("Пожалуйста, введите корректный номер телефона.");
    return;
  }
  
  const form = document.querySelector(".questions__contact-container");
  form.querySelectorAll("input[type='hidden']").forEach(el => el.remove());
  Object.keys(quizAnswers).forEach(key => {
    const hiddenInput = document.createElement("input");
    hiddenInput.type = "hidden";
    hiddenInput.name = key;
    hiddenInput.value = quizAnswers[key];
    form.appendChild(hiddenInput);
  });
  form.submit();
}

/* Price Item Toggle */
document.querySelectorAll(".price__item-button").forEach(el => {
  el.addEventListener("click", () => {
    const infoBlock = el.closest(".price__item").querySelector(".price__item-info");
    infoBlock.classList.toggle("ac-active");
  });
});


/* JavaScript для бургер-меню */
document.addEventListener('DOMContentLoaded', function() {
  // Создаем оверлей для затемнения фона при открытом меню
  const overlay = document.createElement('div');
  overlay.className = 'menu-overlay';
  document.body.appendChild(overlay);

  // Находим необходимые элементы DOM
  const burger = document.querySelector('.burger');
  const headerLower = document.querySelector('.header__lower');
  
  // Создаем блок для контактной информации в мобильном меню
  const mobileContacts = document.createElement('div');
  mobileContacts.className = 'mobile-contacts';
  mobileContacts.innerHTML = `
    <h4 class="mobile-contacts__title">Контактная информация</h4>
    <div class="mobile-contacts__item">
      <svg class="mobile-contacts__icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      <a href="tel:88003008772" class="mobile-contacts__link">8 (800) 300 87 72</a>
    </div>
    <div class="mobile-contacts__item">
      <svg class="mobile-contacts__icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        <polyline points="22,6 12,13 2,6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      <a href="mailto:mail@expertsmet.ru" class="mobile-contacts__link">mail@expertsmet.ru</a>
    </div>
    <div class="mobile-contacts__item">
      <svg class="mobile-contacts__icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        <circle cx="12" cy="10" r="3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      <span class="mobile-contacts__link">Москва, Шелепихинская наб., 34к6</span>
    </div>
    <div class="mobile-contacts__item mobile-button-wrapper">
      <button class="header__upper-button mobile-cta">
        <div class="icon-wrapper">
          <svg class="call-svg" viewBox="0 0 29 26" fill="none">
            <path d="M23.9187 14.2314C23.809 14.0818 23.0798 13.7654 23.0798 13.7654C22.7895 13.6388 20.6537 12.7067 20.2536 12.5744C19.9116 12.4651 19.518 12.3385 19.1696 12.8045C18.905 13.1555 18.1307 13.961 17.8726 14.2142C17.6984 14.3925 17.5306 14.4501 17.137 14.2774C17.0725 14.2487 15.169 13.5237 13.8591 12.4881C12.6976 11.5733 11.8911 10.4398 11.5942 9.99679C11.4136 9.72638 11.5297 9.5998 11.7556 9.39842C11.8911 9.2776 12.4976 8.62745 12.5428 8.56991C12.6396 8.43758 12.8073 8.12689 12.8073 8.12689C12.9815 7.82195 12.8719 7.55728 12.7751 7.37892C12.7041 7.2581 11.6136 4.90489 11.5039 4.68626C11.1942 4.0246 10.8586 3.99007 10.5425 4.00158C10.3876 4.01309 8.93577 4.01884 8.47764 4.46762L8.39376 4.54242C7.94208 4.96818 7 5.85998 7 7.5803C7 7.97729 7.07098 8.39155 7.21939 8.85184C7.4904 9.68035 8.01306 10.5894 8.70993 11.4179C8.72284 11.4352 9.78752 12.747 10.3166 13.2936C11.9943 15.0139 13.8849 16.2854 15.7949 16.9529C18.2339 17.8044 19.2793 18 19.8729 18C20.131 18 20.6795 17.8849 20.7956 17.8734C21.5441 17.8159 23.3121 16.9931 23.6864 16.0668C24.0477 15.1923 24.0542 14.427 23.9187 14.2314Z" fill="#FFE6D8"/>
          </svg>
        </div>
        <span>Заказать звонок</span>
      </button>
    </div>
  `;
  
  headerLower.appendChild(mobileContacts);
  
  // Установка индексов для элементов меню (для анимации)
  const menuItems = document.querySelectorAll('.header__lower-item');
  menuItems.forEach((item, index) => {
    item.style.setProperty('--item-index', index);
  });
  
  // Обработчик клика на бургер
  burger.addEventListener('click', function() {
    this.classList.toggle('active');
    headerLower.classList.toggle('active');
    overlay.classList.toggle('active');
    document.body.classList.toggle('menu-open');
    
    // Добавляем небольшую задержку для запуска анимации элементов меню
    if (headerLower.classList.contains('active')) {
      setTimeout(() => {
        menuItems.forEach(item => {
          item.style.opacity = '1';
          item.style.transform = 'translateX(0)';
        });
      }, 100);
    } else {
      menuItems.forEach(item => {
        item.style.opacity = '0';
        item.style.transform = 'translateX(20px)';
      });
    }
  });
  
  // Закрытие меню при клике на оверлей
  overlay.addEventListener('click', function() {
    burger.classList.remove('active');
    headerLower.classList.remove('active');
    overlay.classList.remove('active');
    document.body.classList.remove('menu-open');
    
    menuItems.forEach(item => {
      item.style.opacity = '0';
      item.style.transform = 'translateX(20px)';
    });
  });
  
  // Закрытие меню при клике на ссылки
  const menuLinks = document.querySelectorAll('.header__lower-link');
  menuLinks.forEach(link => {
    link.addEventListener('click', function() {
      burger.classList.remove('active');
      headerLower.classList.remove('active');
      overlay.classList.remove('active');
      document.body.classList.remove('menu-open');
      
      menuItems.forEach(item => {
        item.style.opacity = '0';
        item.style.transform = 'translateX(20px)';
      });
    });
  });
  
  // Добавляем обработчик для CTA кнопки в мобильном меню
  const mobileCta = document.querySelector('.mobile-cta');
  if (mobileCta) {
    mobileCta.addEventListener('click', function() {
      burger.classList.remove('active');
      headerLower.classList.remove('active');
      overlay.classList.remove('active');
      document.body.classList.remove('menu-open');
    });
  }
  
  // Добавление touch swipe для закрытия меню на мобильных
  let touchStartX = 0;
  let touchEndX = 0;
  
  headerLower.addEventListener('touchstart', e => {
    touchStartX = e.changedTouches[0].screenX;
  }, false);
  
  headerLower.addEventListener('touchend', e => {
    touchEndX = e.changedTouches[0].screenX;
    handleSwipe();
  }, false);
  
  function handleSwipe() {
    if (touchStartX - touchEndX > 50) {  // Свайп влево
      burger.classList.remove('active');
      headerLower.classList.remove('active');
      overlay.classList.remove('active');
      document.body.classList.remove('menu-open');
      
      menuItems.forEach(item => {
        item.style.opacity = '0';
        item.style.transform = 'translateX(20px)';
      });
    }
  }
});


(function() {
    // Функция для показа сообщений
    function showMessage(message, type = 'info') {
        // Удаляем существующие сообщения
        const existingMessages = document.querySelectorAll('.form-message');
        existingMessages.forEach(msg => msg.remove());
        
        // Создаем новое сообщение
        const messageDiv = document.createElement('div');
        messageDiv.className = `form-message form-message-${type}`;
        messageDiv.textContent = message;
        
        // Добавляем стили
        messageDiv.style.cssText = `
            padding: 10px 15px;
            margin: 10px 0;
            border-radius: 5px;
            font-weight: 500;
            text-align: center;
        `;
        
        if (type === 'success') {
            messageDiv.style.backgroundColor = '#d4edda';
            messageDiv.style.color = '#155724';
            messageDiv.style.border = '1px solid #c3e6cb';
        } else if (type === 'error') {
            messageDiv.style.backgroundColor = '#f8d7da';
            messageDiv.style.color = '#721c24';
            messageDiv.style.border = '1px solid #f5c6cb';
        } else {
            messageDiv.style.backgroundColor = '#d1ecf1';
            messageDiv.style.color = '#0c5460';
            messageDiv.style.border = '1px solid #bee5eb';
        }
        
        // Вставляем сообщение после формы
        const form = document.querySelector('form');
        if (form && form.parentNode) {
            form.parentNode.insertBefore(messageDiv, form.nextSibling);
        }
        
        // Автоматически скрываем через 5 секунд
        setTimeout(() => {
            if (messageDiv.parentNode) {
                messageDiv.remove();
            }
        }, 5000);
    }

    // Функция для обработки отправки формы
    function handleFormSubmit(form) {
        form.addEventListener('submit', function(e) {
            // Проверяем, есть ли CSRF токен
            const csrfToken = form.querySelector('[name=csrfmiddlewaretoken]');
            if (!csrfToken || !csrfToken.value) {
                console.warn('CSRF токен не найден, форма будет отправлена обычным способом');
                return; // Позволяем форме отправиться обычным способом
            }
            
            // Проверяем, поддерживает ли форма AJAX
            const formAction = form.getAttribute('action');
            if (!formAction) {
                console.warn('Форма не имеет action, отправляем обычным способом');
                return;
            }
            
            // Показываем индикатор загрузки
            const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
            const originalText = submitBtn?.textContent || 'Отправить';
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.textContent = 'Отправляем...';
            }
            
            // Собираем данные формы
            const formData = new FormData(form);
            
            // Отправляем AJAX запрос
            fetch(formAction, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => {
                if (response.ok) {
                    return response.json().catch(() => ({ success: true }));
                } else {
                    throw new Error(`HTTP ${response.status}`);
                }
            })
            .then(data => {
                if (data.success) {
                    // Успешная отправка
                    form.reset();
                    showMessage('Заявка успешно отправлена!', 'success');
                    
                    // Если это модальная форма, закрываем её
                    const modal = form.closest('.modal');
                    if (modal) {
                        modal.style.display = 'none';
                    }
                } else {
                    // Ошибка от сервера
                    showMessage(data.message || 'Произошла ошибка при отправке', 'error');
                }
            })
            .catch(error => {
                console.error('Ошибка отправки формы:', error);
                showMessage('Произошла ошибка при отправке формы. Попробуйте еще раз.', 'error');
            })
            .finally(() => {
                // Восстанавливаем кнопку
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.textContent = originalText;
                }
            });
        });
    }

    // Инициализация при загрузке страницы
    document.addEventListener('DOMContentLoaded', function() {
        console.log('Инициализация форм...');
        
        // Находим все формы на странице
        const forms = document.querySelectorAll('form');
        console.log(`Найдено форм: ${forms.length}`);
        
        forms.forEach((form, index) => {
            console.log(`Обрабатываем форму ${index + 1}:`, form);
            
            if (form) {
                // Проверяем, есть ли CSRF токен
                const csrfToken = form.querySelector('[name=csrfmiddlewaretoken]');
                if (csrfToken) {
                    console.log(`CSRF токен найден в форме ${index + 1}`);
                    handleFormSubmit(form);
                } else {
                    console.warn(`CSRF токен не найден в форме ${index + 1}, пропускаем`);
                }
            }
        });
    });
})();


console.log("JavaScript подключен к Django!");