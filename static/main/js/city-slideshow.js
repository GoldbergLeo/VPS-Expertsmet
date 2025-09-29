// Динамическая загрузка слайдов для городов
class CitySlideshow {
    constructor() {
        this.currentCity = this.getCurrentCity();
        this.slides = [];
        this.currentSlideIndex = 0;
        this.slideTime = 10000;
        this.slideTimer = 0;
        this.slideInterval = null;
        this.progressInterval = null;
        
        this.init();
    }
    
    getCurrentCity() {
        // Получаем город из data-атрибута или из URL
        const cityElement = document.querySelector('[data-city]');
        if (cityElement) {
            return cityElement.dataset.city;
        }
        
        // Пытаемся определить город из URL
        const hostname = window.location.hostname;
        if (hostname.includes('.')) {
            const subdomain = hostname.split('.')[0];
            if (subdomain !== 'www' && subdomain !== 'expertsmet') {
                return subdomain;
            }
        }
        
        return 'moscow'; // По умолчанию Москва
    }
    
    getCityDisplayName() {
        // 0) Самый высокий приоритет: значения, переданные из шаблона
        if (typeof window !== 'undefined') {
            if (window.CITY_NAME_PREP && String(window.CITY_NAME_PREP).trim()) {
                return String(window.CITY_NAME_PREP).trim();
            }
            if (window.CITY_NAME && String(window.CITY_NAME).trim()) {
                return String(window.CITY_NAME).trim();
            }
        }

        // Сначала пытаемся взять из data-атрибутов шаблона
        const cityElement = document.querySelector('[data-city]');
        if (cityElement) {
            const prep = cityElement.getAttribute('data-city-prep');
            if (prep && prep.trim()) return prep.trim();
            const name = cityElement.getAttribute('data-city-name');
            if (name && name.trim()) return name.trim();
        }

        // Fallback на заранее заданные формы (предложный падеж)
        const cityNames = {
            'moscow': 'Москве',
            'spb': 'Санкт-Петербурге',
            'ekaterinburg': 'Екатеринбурге',
            'novosibirsk': 'Новосибирске',
            'kazan': 'Казани',
            'krasnodar': 'Краснодаре',
            'perm': 'Перми',
            'krasnoyarsk': 'Красноярске',
            'chelyabinsk': 'Челябинске',
            'rostov': 'Ростове-на-Дону',
            'volgograd': 'Волгограде',
            'nizhny-novgorod': 'Нижнем Новгороде',
            'ufa': 'Уфе',
            'tyumen': 'Тюмени',
            'samara': 'Самаре',
            'sochi': 'Сочи',
            'vladikavkaz': 'Владикавказе',
            'arkhangelsk': 'Архангельске',
            'astrakhan': 'Астрахани',
            'barnaul': 'Барнауле',
            'belgorod': 'Белгороде',
            'bryansk': 'Брянске',
            'cheboksary': 'Чебоксарах',
            'ivanovo': 'Иванове',
            'izhevsk': 'Ижевске',
            'kaliningrad': 'Калининграде',
            'kemerovo': 'Кемерово',
            'kirov': 'Кирове',
            'kursk': 'Курске',
            'lipetsk': 'Липецке',
            'magnitogorsk': 'Магнитогорске',
            'makhachkala': 'Махачкале',
            'nizhny-tagil': 'Нижнем Тагиле',
            'novokuznetsk': 'Новокузнецке',
            'omsk': 'Омске',
            'orenburg': 'Оренбурге',
            'penza': 'Пензе',
            'ryazan': 'Рязани',
            'saratov': 'Саратове',
            'stavropol': 'Ставрополе',
            'tver': 'Твери',
            'tomsk': 'Томске',
            'tolyatti': 'Тольятти',
            'ulyanovsk': 'Ульяновске',
            'yaroslavl': 'Ярославле'
        };

        // Если нет формы, возвращаем slug как есть (на крайний случай)
        return cityNames[this.currentCity] || this.currentCity;
    }
    
    async loadSlides() {
        try {
            // 1) Если заданы изображения явно (например, из шаблона), используем их
            if (Array.isArray(window.CITY_HERO_IMAGES) && window.CITY_HERO_IMAGES.length > 0) {
                this.createSlidesFromUrls(window.CITY_HERO_IMAGES);
                this.initSlider();
                return;
            }

            // Проверяем доступность изображений для города
            const availableSlides = await this.checkAvailableSlides();
            
            if (availableSlides.length === 0) {
                // Если нет изображений для города, используем дефолтные
                this.loadDefaultSlides();
                return;
            }
            
            // Создаем слайды для доступных изображений
            this.createSlides(availableSlides);
            this.initSlider();
            
        } catch (error) {
            console.error('Ошибка загрузки слайдов:', error);
            this.loadDefaultSlides();
        }
    }
    
    async checkAvailableSlides() {
        const availableSlides = [];
        const maxSlides = 3; // Максимальное количество слайдов - 3
        const exts = ['webp', 'jpg', 'jpeg'];
        this._resolvedCityImages = {};

        for (let i = 1; i <= maxSlides; i++) {
            let found = false;
            for (const ext of exts) {
                const imgUrl = `/static/main/img/${this.currentCity}/hero_${i}.${ext}`;
                try {
                    const response = await fetch(imgUrl, { method: 'HEAD' });
                    if (response.ok) {
                        availableSlides.push(i);
                        this._resolvedCityImages[i] = imgUrl;
                        found = true;
                        break;
                    }
                } catch (e) {
                    // игнорируем ошибку и пробуем следующее расширение
                }
            }
            // если не нашли — идем к следующему номеру
        }

        return availableSlides;
    }
    
    createSlides(availableSlides) {
        const slideshowContainer = document.getElementById('js-header');
        if (!slideshowContainer) return;
        
        // Очищаем существующие слайды
        slideshowContainer.innerHTML = '';
        
        // Создаем слайды для каждого доступного изображения
        availableSlides.forEach((slideNumber, index) => {
            const slide = this.createSlide(slideNumber, index, availableSlides.length);
            slideshowContainer.appendChild(slide);
        });
        
        // Добавляем навигацию
        this.addNavigation(availableSlides.length);
        
        // Сохраняем ссылки на слайды
        this.slides = Array.from(slideshowContainer.querySelectorAll('.js-slider-home-slide'));
    }

    createSlidesFromUrls(urls) {
        const slideshowContainer = document.getElementById('js-header');
        if (!slideshowContainer) return;

        slideshowContainer.innerHTML = '';

        urls.slice(0, 3).forEach((url, index) => {
            const slide = document.createElement('div');
            slide.className = `slideshow__slide js-slider-home-slide ${index === 0 ? 'is-current' : index === 1 ? 'is-next' : 'is-prev'}`;
            slide.dataset.slide = String(index + 1);

            const titleVariants = [
                `Услуги по составлению<br>сметной документации<br><span class="city-highlight">в ${this.getCityDisplayName()}</span>`,
                `Услуги по разработке<br>строительной документации<br><span class="city-highlight">в ${this.getCityDisplayName()}</span>`,
                `Экспертиза<br>сметной документации<br><span class="city-highlight">в ${this.getCityDisplayName()}</span>`
            ];
            const featuresVariants = [
                ['Локальные сметы базисно-индексным методом', 'Ресурсно-индексный метод расчета', 'Соответствие ФСНБ-2022'],
                ['Сметный аутсорсинг', 'Оптимизация затрат', 'Работаем по всей России'],
                ['Проверка смет', 'Аудит документации', 'Снижение стоимости проекта']
            ];

            const titleIndex = index % titleVariants.length;
            const featuresIndex = index % featuresVariants.length;

            slide.innerHTML = `
                <div class="slideshow__slide-background-parallax background-absolute">
                    <div class="slideshow__slide-background-load-wrap background-absolute">
                        <div class="slideshow__slide-background-load background-absolute">
                            <div class="slideshow__slide-background-wrap background-absolute">
                                <div class="slideshow__slide-background background-absolute">
                                    <div class="slideshow__slide-image-wrap background-absolute">
                                        <div class="slideshow__slide-image background-absolute" style="background-image: url('${url}');"></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="slideshow__slide-caption">
                    <div class="slideshow__slide-caption-text">
                        <div class="container">
                            <div class="hero__inner">
                                <div class="hero__content">
                                    <h1 class="slide__title">${titleVariants[titleIndex]}</h1>
                                    <div class="slide__features">
                                        ${featuresVariants[featuresIndex].map(feature => `<div class=\"feature-item\">${feature}</div>`).join('')}
                                    </div>
                                    <a href="#calculator" class="slide__button">Подробнее</a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;

            slideshowContainer.appendChild(slide);
        });

        this.addNavigation(Math.min(3, urls.length));
        this.slides = Array.from(slideshowContainer.querySelectorAll('.js-slider-home-slide'));
    }
    
    createSlide(slideNumber, index, totalSlides) {
        const slide = document.createElement('div');
        slide.className = `slideshow__slide js-slider-home-slide ${index === 0 ? 'is-current' : index === 1 ? 'is-next' : 'is-prev'}`;
        slide.dataset.slide = slideNumber;
        
        const slideTitles = [
            `Услуги по составлению<br>сметной документации<br><span class="city-highlight">в ${this.getCityDisplayName()}</span>`,
            `Услуги по разработке<br>строительной документации<br><span class="city-highlight">в ${this.getCityDisplayName()}</span>`,
            `Экспертиза<br>сметной документации<br><span class="city-highlight">в ${this.getCityDisplayName()}</span>`,
            `Проверка<br>сметной документации<br><span class="city-highlight">в ${this.getCityDisplayName()}</span>`,
            `Сметный аутсорс<br><span class="city-highlight">в ${this.getCityDisplayName()}</span>`,
            `Консультации по сметам<br><span class="city-highlight">в ${this.getCityDisplayName()}</span>`
        ];
        
        const slideFeatures = [
            ['Локальные сметы базисно-индексным методом', 'Ресурсно-индексный метод расчета', 'Соответствие ФСНБ-2022', 'Корректировка в связи с изменениями в ПД/РД'],
            ['Составление ведомости объемов работ', 'Подготовка исполнительной документации', 'Оформление актов КС-2, КС-3, КС-6', 'Соответствие нормативам и стандартам РФ'],
            ['Проверка соответствия нормативам', 'Анализ обоснованности стоимости', 'Рекомендации по оптимизации', 'Подготовка к прохождению экспертизы'],
            ['Проверка расчетов', 'Анализ обоснованности', 'Рекомендации по корректировке', 'Подготовка документов'],
            ['Полное сопровождение проектов', 'Сметные расчеты', 'Экспертиза документации', 'Консультационная поддержка'],
            ['Профессиональные консультации', 'Анализ проектов', 'Рекомендации по оптимизации', 'Поддержка на всех этапах']
        ];
        
        const titleIndex = (index) % slideTitles.length;
        const featuresIndex = (index) % slideFeatures.length;
        
        const bgUrl = (this._resolvedCityImages && this._resolvedCityImages[slideNumber])
            ? this._resolvedCityImages[slideNumber]
            : `/static/main/img/${this.currentCity}/hero_${slideNumber}.webp`;

        slide.innerHTML = `
            <div class="slideshow__slide-background-parallax background-absolute">
                <div class="slideshow__slide-background-load-wrap background-absolute">
                    <div class="slideshow__slide-background-load background-absolute">
                        <div class="slideshow__slide-background-wrap background-absolute">
                            <div class="slideshow__slide-background background-absolute">
                                <div class="slideshow__slide-image-wrap background-absolute">
                                    <div class="slideshow__slide-image background-absolute"
                                        style="background-image: url('${bgUrl}');">
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="slideshow__slide-caption">
                <div class="slideshow__slide-caption-text">
                    <div class="container">
                        <div class="hero__inner">
                            <div class="hero__content">
                                <h1 class="slide__title">
                                    ${slideTitles[titleIndex]}
                                </h1>
                                <div class="slide__features">
                                    ${slideFeatures[featuresIndex].map(feature => `<div class="feature-item">${feature}</div>`).join('')}
                                </div>
                                <a href="#calculator" class="slide__button">Подробнее</a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        return slide;
    }
    
    addNavigation(totalSlides) {
        const slideshowContainer = document.getElementById('js-header');
        
        const navigation = document.createElement('div');
        navigation.className = 'slideshow__navigation';
        navigation.innerHTML = `
            <div class="slideshow__arrow js-slider-home-prev" id="prev-slide">
                <svg class="arrow-icon" viewBox="0 0 18 18">
                    <path d="M14,0.7L13.3,0L4.7,8.3l0,0L4,9l0,0l0.7,0.7l0,0l8.5,8.3l0.7-0.7L5.4,9L14,0.7z" />
                </svg>
            </div>
            
            <div class="slideshow__indicators">
                ${Array.from({length: totalSlides}, (_, i) => 
                    `<div class="slideshow__indicator ${i === 0 ? 'is-active' : ''}" data-slide="${i}"></div>`
                ).join('')}
            </div>
            
            <div class="slideshow__arrow js-slider-home-next" id="next-slide">
                <svg class="arrow-icon" viewBox="0 0 18 18">
                    <path d="M12.6,9L4,17.3L4.7,18l8.5-8.3l0,0L14,9l0,0l-0.7-0.7l0,0L4.7,0L4,0.7L12.6,9z" />
                </svg>
            </div>
        `;
        
        slideshowContainer.appendChild(navigation);
        
        // Добавляем прогресс-бар
        const progress = document.createElement('div');
        progress.className = 'slideshow__progress';
        progress.innerHTML = '<div class="slideshow__progress-bar" id="slide-progress-bar"></div>';
        slideshowContainer.appendChild(progress);
    }
    
    loadDefaultSlides() {
        // Загружаем дефолтные слайды, если нет городских картинок
        const slideshowContainer = document.getElementById('js-header');
        if (!slideshowContainer) return;

        // Перечень дефолтных изображений (должны существовать в static)
        const defaultImages = [
            '/static/main/img/hero_22.webp',
            '/static/main/img/hero_20.webp',
            '/static/main/img/hero_21.webp'
        ];

        // Очищаем контейнер
        slideshowContainer.innerHTML = '';

        // Создаём слайды на основе дефолтных изображений
        defaultImages.forEach((imgUrl, index) => {
            const slide = document.createElement('div');
            slide.className = `slideshow__slide js-slider-home-slide ${index === 0 ? 'is-current' : index === 1 ? 'is-next' : 'is-prev'}`;
            slide.dataset.slide = String(index + 1);

            const titleVariants = [
                `Услуги по составлению<br>сметной документации<br><span class="city-highlight">в ${this.getCityDisplayName()}</span>`,
                `Услуги по разработке<br>строительной документации<br><span class="city-highlight">в ${this.getCityDisplayName()}</span>`,
                `Экспертиза<br>сметной документации<br><span class="city-highlight">в ${this.getCityDisplayName()}</span>`
            ];

            const featuresVariants = [
                [
                    '<strong>ФСНБ‑2022</strong>, ФЕР, ТЕР',
                    'Сроки от <strong>2 дней</strong>',
                    'Гарантируем прохождение экспертизы'
                ],
                [
                    'Сметный аутсорсинг',
                    'Оптимизация затрат',
                    'Работаем по всей России'
                ],
                [
                    'Проверка смет',
                    'Аудит документации',
                    'Снижение стоимости проекта'
                ]
            ];

            const titleIndex = index % titleVariants.length;
            const featuresIndex = index % featuresVariants.length;

            slide.innerHTML = `
                <div class="slideshow__slide-background-parallax background-absolute">
                    <div class="slideshow__slide-background-load-wrap background-absolute">
                        <div class="slideshow__slide-background-load background-absolute">
                            <div class="slideshow__slide-background-wrap background-absolute">
                                <div class="slideshow__slide-background background-absolute">
                                    <div class="slideshow__slide-image-wrap background-absolute">
                                        <div class="slideshow__slide-image background-absolute" style="background-image: url('${imgUrl}');"></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="slideshow__slide-caption">
                    <div class="slideshow__slide-caption-text">
                        <div class="container">
                            <div class="hero__inner">
                                <div class="hero__content">
                                    <h1 class="slide__title">${titleVariants[titleIndex]}</h1>
                                    <div class="slide__features">
                                        ${featuresVariants[featuresIndex].map(feature => `<div class=\"feature-item\">${feature}</div>`).join('')}
                                    </div>
                                    <a href="#calculator" class="slide__button">Подробнее</a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;

            slideshowContainer.appendChild(slide);
        });

        // Навигация и прогресс
        this.addNavigation(defaultImages.length);
        this.slides = Array.from(slideshowContainer.querySelectorAll('.js-slider-home-slide'));
        this.initSlider();
    }
    
    initSlider() {
        if (this.slides.length === 0) return;
        
        this.showSlide(0);
        this.bindEvents();
        this.startInterval();
    }
    
    bindEvents() {
        const prevBtn = document.querySelector('.js-slider-home-prev');
        const nextBtn = document.querySelector('.js-slider-home-next');
        const indicators = document.querySelectorAll('.slideshow__indicator');
        
        if (prevBtn) {
            prevBtn.addEventListener('click', () => {
                this.showSlide(this.currentSlideIndex - 1);
                this.resetInterval();
            });
        }
        
        if (nextBtn) {
            nextBtn.addEventListener('click', () => {
                this.showSlide(this.currentSlideIndex + 1);
                this.resetInterval();
            });
        }
        
        indicators.forEach((indicator, index) => {
            indicator.addEventListener('click', () => {
                this.showSlide(index);
                this.resetInterval();
            });
        });
    }
    
    showSlide(n) {
        this.currentSlideIndex = n;
        
        if (this.currentSlideIndex >= this.slides.length) this.currentSlideIndex = 0;
        if (this.currentSlideIndex < 0) this.currentSlideIndex = this.slides.length - 1;
        
        // Убираем все классы состояния
        this.slides.forEach(slide => {
            slide.classList.remove('is-current', 'is-next', 'is-prev');
        });
        
        // Устанавливаем классы для текущего, следующего и предыдущего слайдов
        this.slides[this.currentSlideIndex].classList.add('is-current');
        
        let nextIndex = (this.currentSlideIndex + 1) % this.slides.length;
        this.slides[nextIndex].classList.add('is-next');
        
        let prevIndex = (this.currentSlideIndex + this.slides.length - 1) % this.slides.length;
        this.slides[prevIndex].classList.add('is-prev');
        
        // Обновляем индикаторы
        this.setActiveIndicator(this.currentSlideIndex);
        
        // Запускаем прогресс-бар
        this.startProgressBar();
    }
    
    setActiveIndicator(index) {
        const indicators = document.querySelectorAll('.slideshow__indicator');
        indicators.forEach(indicator => indicator.classList.remove('is-active'));
        if (indicators[index]) {
            indicators[index].classList.add('is-active');
        }
    }
    
    startProgressBar() {
        this.slideTimer = 0;
        const progressBar = document.getElementById('slide-progress-bar');
        if (!progressBar) return;
        
        progressBar.style.width = '0%';
        
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
        }
        
        this.progressInterval = setInterval(() => {
            this.slideTimer += 50;
            const percentage = (this.slideTimer / this.slideTime) * 100;
            progressBar.style.width = `${percentage}%`;
            
            if (this.slideTimer >= this.slideTime) {
                clearInterval(this.progressInterval);
            }
        }, 50);
    }
    
    startInterval() {
        this.slideInterval = setInterval(() => {
            this.showSlide(this.currentSlideIndex + 1);
        }, this.slideTime);
    }
    
    resetInterval() {
        if (this.slideInterval) {
            clearInterval(this.slideInterval);
            this.startInterval();
        }
    }
    
    init() {
        const run = () => this.loadSlides();
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', run);
        } else {
            run();
        }
    }
}

// Инициализация слайдера
new CitySlideshow();
