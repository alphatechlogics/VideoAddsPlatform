// Configuration
let API_BASE_URL = 'http://localhost:8000';

// DOM Elements
const searchForm = document.getElementById('searchForm');
const searchStatus = document.getElementById('searchStatus');
const loading = document.getElementById('loading');
const error = document.getElementById('error');
const videoGrid = document.getElementById('videoGrid');
const messages = document.getElementById('messages');
const apiBaseUrl = document.getElementById('apiBaseUrl');
const apiToken = document.getElementById('apiToken');

// Show message function
function showMessage(message, type = 'success') {
    messages.innerHTML = `<div class="alert alert-${type}">${message}</div>`;
    messages.style.display = 'block';
    setTimeout(() => {
        messages.style.display = 'none';
    }, 5000);
}

// Format number with commas
function formatNumber(num) {
    if (!num) return '0';
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// Format duration
function formatDuration(duration) {
    if (!duration) return 'N/A';
    return duration;
}

// Format date
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    try {
        return new Date(dateString).toLocaleDateString();
    } catch (e) {
        return dateString;
    }
}

// Create video card HTML
function createVideoCard(video) {
    return `
        <div class="video-card">
            ${video.thumbnail ? `<img src="${video.thumbnail}" alt="${video.title || 'Video thumbnail'}" class="thumbnail" onerror="this.style.display='none'">` : ''}
            <div class="video-info">
                <h3>${video.title || 'Untitled Video'}</h3>
                <div class="video-meta">
                </div>
                <span class="category-badge">${video.category || 'Uncategorized'}</span>
                <a href="${video.url || video.video_url || '#'}" target="_blank" class="watch-button">Watch Video</a>
            </div>
        </div>
    `;
}

// API request helper
async function makeApiRequest(endpoint, params = {}) {
    const url = new URL(endpoint, API_BASE_URL);
    
    // Add query parameters
    Object.keys(params).forEach(key => {
        if (params[key]) {
            url.searchParams.append(key, params[key]);
        }
    });

    const headers = {};

    // Add authorization header if token is provided
    if (apiToken.value) {
        headers['Authorization'] = `Bearer ${apiToken.value}`;
    }

    const response = await fetch(url, {
        method: 'GET',
        headers: headers,
        mode: 'cors',
    });

    if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return await response.json();
}

// Load categories from API
async function loadCategories() {
    try {
        const data = await makeApiRequest('/api/categories/');
        const categorySelect = document.getElementById('category');
        
        // Clear existing options except "All Categories"
        categorySelect.innerHTML = '<option value="">All Categories</option>';
        
        // Handle different response formats
        let categories = [];
        if (Array.isArray(data)) {
            categories = data;
        } else if (data.results) {
            categories = data.results;
        } else if (data.data) {
            categories = data.data;
        } else if (data.categories) {
            categories = data.categories;
        }

        // Add categories to select
        categories.forEach(category => {
            const option = document.createElement('option');
            if (typeof category === 'object') {
                option.value = category.id || category.value || category.name;
                option.textContent = category.name || category.label || category.title;
            } else {
                option.value = category;
                option.textContent = category;
            }
            categorySelect.appendChild(option);
        });

        console.log('Categories loaded successfully');
    } catch (err) {
        console.warn('Failed to load categories:', err.message);
        // Keep default categories if API fails
    }
}

// Handle search form submission
searchForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const keyword = document.getElementById('keyword').value.trim();
    const channelId = document.getElementById('channel_id').value.trim();
    const category = document.getElementById('category').value;
    
    // Validate inputs
    if (!keyword && !channelId && !category) {
        showMessage('Please enter at least one search criteria', 'error');
        return;
    }

    if (!API_BASE_URL) {
        showMessage('Please configure the API base URL', 'error');
        return;
    }
    
    // Show loading state
    loading.style.display = 'block';
    error.style.display = 'none';
    videoGrid.innerHTML = '';
    searchStatus.style.display = 'none';

    try {
        const searchParams = {
            keyword: keyword,
            channel_id: channelId,
            category: category
        };

        // Use only the specific endpoint
        const data = await makeApiRequest('/api/search-unlisted/', searchParams);

        loading.style.display = 'none';

        // Handle different response formats
        let videos = [];
        if (data.status === 'success' && data.data) {
            videos = Array.isArray(data.data) ? data.data : [data.data];
        } else if (data.results) {
            videos = Array.isArray(data.results) ? data.results : [data.results];
        } else if (Array.isArray(data)) {
            videos = data;
        } else if (data.videos) {
            videos = Array.isArray(data.videos) ? data.videos : [data.videos];
        } else {
            throw new Error('Invalid response format');
        }

        searchStatus.textContent = `Found ${videos.length} video${videos.length !== 1 ? 's' : ''}`;
        searchStatus.style.display = 'block';

        if (videos.length > 0) {
            videoGrid.innerHTML = videos.map(createVideoCard).join('');
            showMessage(`Successfully loaded ${videos.length} videos`);
        } else {
            videoGrid.innerHTML = '<div class="no-results"><p>No videos found matching your criteria.</p></div>';
        }
    } catch (err) {
        loading.style.display = 'none';
        error.textContent = `Error: ${err.message}`;
        error.style.display = 'block';
        console.error('Search error:', err);
        showMessage(`Search failed: ${err.message}`, 'error');
    }
});

// Load sample data on page load for demo purposes
window.addEventListener('load', async () => {
    showMessage('Video search application loaded. Loading categories...');
    
    // Update API base URL from input field if provided
    apiBaseUrl.addEventListener('change', () => {
        API_BASE_URL = apiBaseUrl.value.trim();
    });
    
    // Load categories from API
    await loadCategories();
    
    showMessage('Application ready! Configure your API settings if needed and start searching!');
});
