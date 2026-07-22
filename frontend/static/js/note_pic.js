let cachedImages = [];
let currentUser = null;
let emblaApi = null;

// Toast notification helpers
function showToast(message, type) {
    const toast = document.getElementById('toast-message');
    toast.textContent = message;
    toast.className = `toast ${type}`;
    toast.classList.remove('hidden');
    setTimeout(hideToast, 3000);
}

function showStickyToast(message, type) {
    const toast = document.getElementById('toast-message');
    toast.textContent = message;
    toast.className = `toast ${type}`;
    toast.classList.remove('hidden');
}

function hideToast() {
    const toast = document.getElementById('toast-message');
    toast.className = 'toast hidden';
}

// --- PROFILE LOADING ---
async function loadProfile() {
    try {
        const response = await fetch('/api/user/profile');
        if (response.ok) {
            const result = await response.json();
            currentUser = result.user;
        } else if (response.status === 401) {
            window.location.href = '/';
        }
    } catch (err) {
        console.error("Error loading user profile", err);
    }
}

// --- FETCH IMAGES (EMBLA CAROUSEL SYSTEM) ---
async function fetchImages() {
    const container = document.getElementById('emblaContainer');
    const carouselWrapper = document.getElementById('emblaCarousel');
    const emptyState = document.getElementById('imageEmptyState');
    
    // Clean up old Embla instance if it exists
    if (emblaApi) {
        emblaApi.destroy();
        emblaApi = null;
    }
    container.innerHTML = '';
    
    try {
        const response = await fetch('/api/images');
        if (response.ok) {
            const result = await response.json();
            cachedImages = result.images;
            
            if (cachedImages.length === 0) {
                emptyState.style.display = 'block';
                carouselWrapper.style.display = 'none';
                return;
            }
            emptyState.style.display = 'none';
            carouselWrapper.style.display = 'block';

            cachedImages.forEach((item) => {
                const slide = document.createElement('div');
                slide.className = 'embla__slide';
                slide.id = `img-slide-${item.id}`;
                
                const uploadUrl = `/static/uploads/${item.filename}`;

                slide.innerHTML = `
                    <button class="embla__delete-btn" onclick="event.stopPropagation(); deleteImageRecord(${item.id})">
                        <i class="fas fa-trash-alt"></i>
                    </button>
                    <div class="embla__card-inner" onclick="openLightbox('${uploadUrl}')">
                        <img src="${uploadUrl}" alt="${item.original_name}" loading="lazy">
                    </div>
                    <div class="embla__title-label">
                        ${item.original_name}
                    </div>
                `;
                container.appendChild(slide);
            });
            
            // Initialize Embla Carousel API
            initEmblaCarousel();
        }
    } catch (err) {
        console.error("Error retrieving images", err);
        showToast("Failed to fetch secure images.", "error");
    }
}

// --- EMBLA CAROUSEL INITIALIZATION & CONTROLS ---
function initEmblaCarousel() {
    const emblaNode = document.getElementById('emblaViewport');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const dotsContainer = document.getElementById('emblaDots');
    
    dotsContainer.innerHTML = '';

    // Initialize Embla API
    emblaApi = EmblaCarousel(emblaNode, {
        loop: true,
        slidesToScroll: 1,
        align: 'center'
    });

    const slides = emblaApi.slideNodes();
    
    // Generate Pagination Dots
    slides.forEach((_, idx) => {
        const dot = document.createElement('button');
        dot.className = 'embla__dot';
        dot.ariaLabel = `Go to slide ${idx + 1}`;
        dot.addEventListener('click', () => emblaApi.scrollTo(idx));
        dotsContainer.appendChild(dot);
    });

    // Update selected class on snaps
    const updateClasses = () => {
        const selectedIdx = emblaApi.selectedScrollSnap();
        
        // Toggle slide active classes
        slides.forEach((slide, idx) => {
            if (idx === selectedIdx) {
                slide.classList.add('is-selected');
            } else {
                slide.classList.remove('is-selected');
            }
        });

        // Toggle dots active classes
        const dots = dotsContainer.querySelectorAll('.embla__dot');
        dots.forEach((dot, idx) => {
            if (idx === selectedIdx) {
                dot.classList.add('is-selected');
            } else {
                dot.classList.remove('is-selected');
            }
        });
    };

    // Set up event listeners
    emblaApi.on('select', updateClasses);
    emblaApi.on('init', updateClasses);
    
    prevBtn.addEventListener('click', () => emblaApi.scrollPrev());
    nextBtn.addEventListener('click', () => emblaApi.scrollNext());

    // Run initial class assignment
    updateClasses();
}

// --- UPLOAD IMAGE ---
async function uploadImage(file) {
    if (!file) return;

    const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
        showToast("Invalid file type. Please upload an image.", "error");
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
        showStickyToast("Uploading secure image...", "success");
        const response = await fetch('/api/images', {
            method: 'POST',
            body: formData
        });
        const result = await response.json();
        if (response.ok) {
            showToast("Image uploaded successfully!", 'success');
            fetchImages();
        } else {
            showToast(result.message || "Failed to save image.", 'error');
        }
    } catch (err) {
        console.error(err);
        showToast("Failed to upload image.", "error");
    }
}

// --- DELETE IMAGE ---
async function deleteImageRecord(id) {
    if (!confirm("Are you sure you want to delete this secure document/image permanently?")) return;

    try {
        const response = await fetch(`/api/images/${id}`, {
            method: 'DELETE'
        });
        const result = await response.json();
        if (response.ok) {
            showToast(result.message, 'success');
            fetchImages();
        } else {
            showToast(result.message, 'error');
        }
    } catch (err) {
        console.error(err);
        showToast("Failed to delete record.", "error");
    }
}

// --- FILTER IMAGES ---
function filterImages() {
    const query = document.getElementById('searchImages').value.toLowerCase();
    const container = document.getElementById('emblaContainer');
    const carouselWrapper = document.getElementById('emblaCarousel');
    const emptyState = document.getElementById('imageEmptyState');
    
    // Clean up old Embla instance if it exists
    if (emblaApi) {
        emblaApi.destroy();
        emblaApi = null;
    }
    container.innerHTML = '';
    
    const filtered = cachedImages.filter(item => item.original_name.toLowerCase().includes(query));
    
    if (filtered.length === 0) {
        emptyState.style.display = 'block';
        carouselWrapper.style.display = 'none';
        return;
    }
    emptyState.style.display = 'none';
    carouselWrapper.style.display = 'block';

    filtered.forEach((item) => {
        const slide = document.createElement('div');
        slide.className = 'embla__slide';
        slide.id = `img-slide-${item.id}`;
        
        const uploadUrl = `/static/uploads/${item.filename}`;

        slide.innerHTML = `
            <button class="embla__delete-btn" onclick="event.stopPropagation(); deleteImageRecord(${item.id})">
                <i class="fas fa-trash-alt"></i>
            </button>
            <div class="embla__card-inner" onclick="openLightbox('${uploadUrl}')">
                <img src="${uploadUrl}" alt="${item.original_name}" loading="lazy">
            </div>
            <div class="embla__title-label">
                ${item.original_name}
            </div>
        `;
        container.appendChild(slide);
    });
    
    // Re-initialize Embla API
    initEmblaCarousel();
}

// --- LIGHTBOX FUNCTIONS ---
function openLightbox(src) {
    const modal = document.getElementById('lightbox');
    const img = document.getElementById('lightboxImg');
    img.src = src;
    modal.classList.add('active');
}

// --- LIGHTBOX CLOSE ---
function closeLightbox() {
    document.getElementById('lightbox').classList.remove('active');
}

// --- LOGOUT CONTROLLER ---
async function handleLogout() {
    if (!confirm("Confirm logging out of VaultSync?")) return;
    try {
        const response = await fetch('/api/logout', { method: 'POST' });
        const result = await response.json();
        if (response.ok) {
            localStorage.removeItem('currentUser');
            window.location.href = result.redirect;
        }
    } catch (err) {
        console.error("Logout failed", err);
    }
}

// --- DRAG & DROP EVENT LISTENERS ---
const dropZone = document.getElementById('dropZone');

['dragenter', 'dragover'].forEach(eventName => {
    dropZone.addEventListener(eventName, (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    }, false);
});

['dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
    }, false);
});

dropZone.addEventListener('drop', (e) => {
    const dt = e.dataTransfer;
    const files = dt.files;
    if (files.length > 0) {
        uploadImage(files[0]);
    }
}, false);

// Run on Mount
window.addEventListener('DOMContentLoaded', () => {
    loadProfile();
    fetchImages();
});