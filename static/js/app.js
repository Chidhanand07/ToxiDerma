// ===== TOXIDERMA-XAI APPLICATION JavaScript =====
// Complete working implementation with all features

class ToxiDermaApp {
    constructor() {
        // DOM Elements
        this.fileInput = document.getElementById('fileInput');
        this.uploadZone = document.getElementById('uploadZone');
        this.uploadPreview = document.getElementById('uploadPreview');
        this.previewImage = document.getElementById('previewImage');
        this.analyzeBtn = document.getElementById('analyzeBtn');
        this.resetBtn = document.getElementById('resetBtn');
        this.loadingSection = document.getElementById('loadingSection');
        this.resultsSection = document.getElementById('resultsSection');
        
        // State
        this.selectedFile = null;
        
        // Initialize
        this.init();
    }
    
    init() {
        console.log('🚀 ToxiDerma-XAI Application Starting...');
        this.setupEventListeners();
        this.setupSmoothScrolling();
        this.setupTabSwitching();
        this.setupNavbarScroll();
        console.log('✅ Application Initialized Successfully!');
    }
    
    // ===== EVENT LISTENERS =====
    setupEventListeners() {
        // File input change
        this.fileInput.addEventListener('change', (e) => {
            console.log('📁 File input changed');
            this.handleFileSelect(e);
        });
        
        // Upload zone click
        this.uploadZone.addEventListener('click', () => {
            console.log('🖱️ Upload zone clicked');
            this.fileInput.click();
        });
        
        // Drag and drop
        this.uploadZone.addEventListener('dragover', (e) => this.handleDragOver(e));
        this.uploadZone.addEventListener('dragleave', (e) => this.handleDragLeave(e));
        this.uploadZone.addEventListener('drop', (e) => this.handleFileDrop(e));
        
        // Action buttons
        this.analyzeBtn.addEventListener('click', () => {
            console.log('🧠 Analyze button clicked');
            this.analyzeImage();
        });
        
        this.resetBtn.addEventListener('click', () => {
            console.log('🔄 Reset button clicked');
            this.resetUpload();
        });
        
        // Result action buttons
        const downloadBtn = document.getElementById('downloadReport');
        const newAnalysisBtn = document.getElementById('newAnalysis');
        
        if (downloadBtn) {
            downloadBtn.addEventListener('click', () => {
                console.log('💾 Download report clicked');
                this.downloadReport();
            });
        }
        
        if (newAnalysisBtn) {
            newAnalysisBtn.addEventListener('click', () => {
                console.log('🆕 New analysis clicked');
                this.resetUpload();
            });
        }
    }
    
    // ===== SMOOTH SCROLLING =====
    setupSmoothScrolling() {
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const targetId = link.getAttribute('href').substring(1);
                const targetElement = document.getElementById(targetId);
                
                if (targetElement) {
                    targetElement.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                    
                    // Update active link
                    document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
                    link.classList.add('active');
                }
            });
        });
    }
    
    // ===== TAB SWITCHING =====
    setupTabSwitching() {
        document.querySelectorAll('.viz-tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                const tabName = e.currentTarget.getAttribute('data-tab');
                console.log(`🔄 Switching to ${tabName} tab`);
                this.switchTab(tabName);
            });
        });
    }
    
    switchTab(tabName) {
        // Remove active class from all tabs and panels
        document.querySelectorAll('.viz-tab').forEach(tab => tab.classList.remove('active'));
        document.querySelectorAll('.viz-panel').forEach(panel => panel.classList.remove('active'));
        
        // Add active class to selected tab and panel
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
        document.getElementById(`${tabName}Viz`).classList.add('active');
    }
    
    // ===== NAVBAR SCROLL EFFECT =====
    setupNavbarScroll() {
        window.addEventListener('scroll', () => {
            const navbar = document.querySelector('.navbar');
            if (window.scrollY > 50) {
                navbar.style.background = 'rgba(10, 14, 26, 0.98)';
                navbar.style.boxShadow = '0 4px 30px rgba(0, 0, 0, 0.3)';
            } else {
                navbar.style.background = 'rgba(10, 14, 26, 0.95)';
                navbar.style.boxShadow = 'none';
            }
        });
    }
    
    // ===== FILE HANDLING =====
    handleFileSelect(e) {
        const file = e.target.files[0];
        if (file) {
            console.log(`📄 File selected: ${file.name}, Size: ${(file.size / 1024).toFixed(2)} KB`);
            this.processSelectedFile(file);
        }
    }
    
    handleDragOver(e) {
        e.preventDefault();
        e.stopPropagation();
        this.uploadZone.classList.add('dragover');
    }
    
    handleDragLeave(e) {
        e.preventDefault();
        e.stopPropagation();
        this.uploadZone.classList.remove('dragover');
    }
    
    handleFileDrop(e) {
        e.preventDefault();
        e.stopPropagation();
        this.uploadZone.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            console.log(`📋 File dropped: ${files[0].name}`);
            this.processSelectedFile(files[0]);
        }
    }
    
    processSelectedFile(file) {
        // Validate file type
        const validTypes = ['image/jpeg', 'image/jpg', 'image/png'];
        if (!validTypes.includes(file.type)) {
            this.showError('❌ Invalid file type. Please select JPG, JPEG, or PNG image.');
            return;
        }
        
        // Validate file size (10MB)
        const maxSize = 10 * 1024 * 1024;
        if (file.size > maxSize) {
            this.showError('❌ File size too large. Maximum size is 10MB.');
            return;
        }
        
        this.selectedFile = file;
        this.displayPreview(file);
    }
    
    displayPreview(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            console.log('🖼️ Displaying image preview');
            this.previewImage.src = e.target.result;
            this.uploadZone.style.display = 'none';
            this.uploadPreview.classList.remove('hidden');
        };
        reader.readAsDataURL(file);
    }
    
    // ===== IMAGE ANALYSIS =====
    analyzeImage() {
        if (!this.selectedFile) {
            this.showError('❌ Please select an image first');
            return;
        }
        
        console.log('🔬 Starting image analysis...');
        
        // Hide preview, show loading
        this.uploadPreview.classList.add('hidden');
        this.loadingSection.classList.remove('hidden');
        this.resultsSection.classList.add('hidden');
        
        // Start loading animation
        this.startLoadingAnimation();
        
        // Create form data
        const formData = new FormData();
        formData.append('file', this.selectedFile);
        
        // Send to backend
        fetch('/predict', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            console.log(`📡 Response status: ${response.status}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('✅ Analysis complete:', data);
            this.handleAnalysisResult(data);
        })
        .catch(error => {
            console.error('❌ Analysis error:', error);
            this.showError(`Analysis failed: ${error.message}`);
            this.hideLoading();
        });
    }
    
    startLoadingAnimation() {
        const progressFill = document.getElementById('progressFill');
        const loadingStatus = document.getElementById('loadingStatus');
        
        const steps = [
            'Initializing AI model...',
            'Processing image data...',
            'Running deep learning analysis...',
            'Extracting features...',
            'Generating Grad-CAM visualization...',
            'Creating LIME explanations...',
            'Finalizing results...'
        ];
        
        let currentStep = 0;
        let progress = 0;
        
        const updateProgress = () => {
            if (progress < 95) {
                progress += Math.random() * 12;
                const currentProgress = Math.min(progress, 95);
                progressFill.style.width = `${currentProgress}%`;
                
                const stepIndex = Math.floor((currentProgress / 95) * steps.length);
                if (stepIndex < steps.length && stepIndex !== currentStep) {
                    currentStep = stepIndex;
                    loadingStatus.textContent = steps[currentStep];
                    console.log(`⏳ ${steps[currentStep]}`);
                }
                
                setTimeout(updateProgress, 400 + Math.random() * 800);
            }
        };
        
        updateProgress();
    }
    
    handleAnalysisResult(data) {
        if (data.success) {
            console.log('✅ Displaying results');
            this.displayResults(data);
        } else {
            console.error('❌ Analysis failed:', data.error);
            this.showError(data.error || 'Analysis failed');
            this.hideLoading();
        }
    }
    
    displayResults(data) {
        // Complete the progress bar
        const progressFill = document.getElementById('progressFill');
        const loadingStatus = document.getElementById('loadingStatus');
        
        progressFill.style.width = '100%';
        loadingStatus.textContent = 'Analysis complete! ✓';
        
        // Wait a moment then show results
        setTimeout(() => {
            this.hideLoading();
            this.showResults(data);
        }, 1000);
    }
    
    showResults(data) {
        console.log('📊 Populating results UI');
        
        // Get DOM elements
        const predictionLabel = document.getElementById('predictionLabel');
        const statusBadge = document.getElementById('statusBadge');
        const confidenceBar = document.getElementById('confidenceBar');
        const confidenceValue = document.getElementById('confidenceValue');
        const probAffected = document.getElementById('probAffected');
        const probHealthy = document.getElementById('probHealthy');
        const explanationText = document.getElementById('explanationText');
        const gradcamImage = document.getElementById('gradcamImage');
        const limeImage = document.getElementById('limeImage');
        
        // Update prediction
        predictionLabel.textContent = data.prediction;
        statusBadge.textContent = data.prediction;
        statusBadge.className = `status-badge ${data.prediction.toLowerCase()}`;
        
        // Update confidence
        const confidence = Math.round(data.confidence * 100);
        confidenceValue.textContent = `${confidence}%`;
        
        // Animate confidence bar
        setTimeout(() => {
            confidenceBar.style.width = `${confidence}%`;
        }, 200);
        
        // Update probabilities
        if (data.probabilities) {
            probAffected.textContent = `${Math.round(data.probabilities.Affected * 100)}%`;
            probHealthy.textContent = `${Math.round(data.probabilities.Healthy * 100)}%`;
        }
        
        // Update explanation
        if (data.explanation) {
            explanationText.textContent = data.explanation;
        } else {
            explanationText.textContent = `The AI model has classified this image as ${data.prediction.toLowerCase()} with ${confidence}% confidence. The highlighted regions show the areas that most influenced this decision.`;
        }
        
        // Update visualization images
        if (data.gradcam_image) {
            gradcamImage.src = `data:image/png;base64,${data.gradcam_image}`;
            console.log('🔥 Grad-CAM visualization loaded');
        } else {
            gradcamImage.src = '';
            gradcamImage.alt = 'Grad-CAM visualization not available';
        }
        
        if (data.lime_image) {
            limeImage.src = `data:image/png;base64,${data.lime_image}`;
            console.log('🧩 LIME visualization loaded');
        } else {
            limeImage.src = '';
            limeImage.alt = 'LIME visualization not available';
        }
        
        // Show results section
        this.resultsSection.classList.remove('hidden');
        
        // Scroll to results
        setTimeout(() => {
            this.resultsSection.scrollIntoView({ 
                behavior: 'smooth',
                block: 'start'
            });
        }, 300);
        
        console.log('✅ Results displayed successfully');
    }
    
    // ===== RESET FUNCTION =====
    resetUpload() {
        console.log('🔄 Resetting application');
        
        // Reset UI
        this.uploadZone.style.display = 'block';
        this.uploadPreview.classList.add('hidden');
        this.loadingSection.classList.add('hidden');
        this.resultsSection.classList.add('hidden');
        
        // Reset state
        this.selectedFile = null;
        this.fileInput.value = '';
        this.previewImage.src = '';
        
        // Reset progress
        const progressFill = document.getElementById('progressFill');
        if (progressFill) {
            progressFill.style.width = '0%';
        }
        
        // Scroll to upload section
        document.getElementById('upload').scrollIntoView({ 
            behavior: 'smooth',
            block: 'start'
        });
        
        console.log('✅ Application reset complete');
    }
    
    hideLoading() {
        this.loadingSection.classList.add('hidden');
        this.uploadPreview.classList.remove('hidden');
    }
    
    // ===== DOWNLOAD REPORT =====
    downloadReport() {
        console.log('💾 Generating report...');
        
        try {
            const reportData = {
                prediction: document.getElementById('predictionLabel').textContent,
                confidence: document.getElementById('confidenceValue').textContent,
                probabilities: {
                    affected: document.getElementById('probAffected').textContent,
                    healthy: document.getElementById('probHealthy').textContent
                },
                explanation: document.getElementById('explanationText').textContent,
                timestamp: new Date().toISOString(),
                analyzedImage: this.selectedFile ? this.selectedFile.name : 'unknown'
            };
            
            // Create and download JSON file
            const blob = new Blob([JSON.stringify(reportData, null, 2)], { 
                type: 'application/json' 
            });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `toxiderma_analysis_${Date.now()}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            
            this.showSuccess('✅ Report downloaded successfully!');
            console.log('✅ Report downloaded');
        } catch (error) {
            console.error('❌ Download error:', error);
            this.showError('Failed to download report');
        }
    }
    
    // ===== NOTIFICATION SYSTEM =====
    showError(message) {
        this.showNotification(message, 'error');
    }
    
    showSuccess(message) {
        this.showNotification(message, 'success');
    }
    
    showNotification(message, type = 'error') {
        console.log(`📢 Notification (${type}): ${message}`);
        
        // Remove any existing notifications
        const existing = document.querySelector('.notification');
        if (existing) {
            existing.remove();
        }
        
        // Create notification
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        
        const icon = type === 'error' ? 'fa-exclamation-circle' : 'fa-check-circle';
        const bgColor = type === 'error' ? 
            'linear-gradient(135deg, #ef4444, #dc2626)' : 
            'linear-gradient(135deg, #10b981, #059669)';
        
        notification.innerHTML = `
            <div style="display: flex; align-items: center; gap: 12px;">
                <i class="fas ${icon}" style="font-size: 1.2rem;"></i>
                <span>${message}</span>
            </div>
            <button class="notification-close" style="background: none; border: none; color: white; font-size: 1.3rem; cursor: pointer; margin-left: 15px;">
                &times;
            </button>
        `;
        
        notification.style.cssText = `
            position: fixed;
            top: 100px;
            right: 20px;
            background: ${bgColor};
            color: white;
            padding: 16px 20px;
            border-radius: 12px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            z-index: 10000;
            display: flex;
            align-items: center;
            justify-content: space-between;
            min-width: 300px;
            max-width: 500px;
            animation: slideInRight 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            backdrop-filter: blur(10px);
        `;
        
        document.body.appendChild(notification);
        
        // Close button
        notification.querySelector('.notification-close').addEventListener('click', () => {
            notification.style.animation = 'slideOutRight 0.3s ease forwards';
            setTimeout(() => notification.remove(), 300);
        });
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.style.animation = 'slideOutRight 0.3s ease forwards';
                setTimeout(() => notification.remove(), 300);
            }
        }, 5000);
    }
}

// ===== CSS ANIMATIONS =====
const animationStyles = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutRight {
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
`;

// Add animations to document
const styleSheet = document.createElement('style');
styleSheet.textContent = animationStyles;
document.head.appendChild(styleSheet);

// ===== INITIALIZE APPLICATION =====
document.addEventListener('DOMContentLoaded', () => {
    console.log('🎯 DOM Content Loaded');
    
    // Create and initialize app
    window.toxiDermaApp = new ToxiDermaApp();
    
    console.log('🎉 ToxiDerma-XAI Ready!');
});

// ===== GLOBAL ERROR HANDLER =====
window.addEventListener('error', (e) => {
    console.error('💥 Global error:', e.error);
});

// Log when page is fully loaded
window.addEventListener('load', () => {
    console.log('✨ Page fully loaded and ready!');
});