/**
 * AI Academic Support — Main JavaScript
 * 
 * Handles:
 * - Sending questions to the Flask backend via fetch()
 * - Uploading images for AI analysis
 * - Rendering Mermaid.js diagrams
 * - Displaying results in card format
 * - Error handling and loading states
 * - Mobile navigation toggle
 */

// ============================================================
// INITIALIZATION
// ============================================================

// Initialize Mermaid.js with safe settings
mermaid.initialize({
    startOnLoad: false,
    theme: 'default',
    securityLevel: 'strict',
    flowchart: {
        useMaxWidth: true,
        htmlLabels: false
    }
});

// Track selected image file for upload
let selectedImageFile = null;

// ============================================================
// NAVIGATION
// ============================================================

// Mobile menu toggle
document.getElementById('navToggle').addEventListener('click', function () {
    document.getElementById('navLinks').classList.toggle('open');
});

// Close mobile menu when a link is clicked
document.querySelectorAll('.nav-link').forEach(function (link) {
    link.addEventListener('click', function () {
        document.getElementById('navLinks').classList.remove('open');

        // Update active state
        document.querySelectorAll('.nav-link').forEach(function (l) {
            l.classList.remove('active');
        });
        this.classList.add('active');
    });
});

// Navbar scroll effect
window.addEventListener('scroll', function () {
    var navbar = document.getElementById('navbar');
    if (window.scrollY > 60) {
        navbar.classList.add('scrolled');
    } else {
        navbar.classList.remove('scrolled');
    }
});

// Allow submitting question with Ctrl+Enter
document.getElementById('questionInput').addEventListener('keydown', function (e) {
    if (e.ctrlKey && e.key === 'Enter') {
        askQuestion();
    }
});

// ============================================================
// QUESTION HANDLING
// ============================================================

/**
 * Set an example question into the textarea.
 */
function setExample(text) {
    document.getElementById('questionInput').value = text;
    document.getElementById('questionInput').focus();
}

/**
 * Clear the question textarea and hide results.
 */
function clearQuestion() {
    document.getElementById('questionInput').value = '';
    hideElement('questionResults');
    hideElement('questionError');
    hideElement('questionLoading');
    document.getElementById('questionInput').focus();
}

function searchWikipedia() {
    var query = document.getElementById('wikiInput').value.trim();
    if (!query) {
        showError('wikiError', 'wikiErrorText', 'Please enter a topic to search on Wikipedia.');
        return;
    }

    showElement('wikiLoading');
    hideElement('wikiError');
    hideElement('wikiResults');

    fetch('/wiki', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: query })
    })
        .then(function (response) {
            return response.json().then(function (data) {
                return { ok: response.ok, data: data };
            });
        })
        .then(function (result) {
            hideElement('wikiLoading');
            if (!result.ok || result.data.error) {
                showError('wikiError', 'wikiErrorText', result.data.error || 'Wikipedia lookup failed.');
                return;
            }

            document.getElementById('wikiTitle').textContent = result.data.title || 'Wikipedia Result';
            document.getElementById('wikiDescription').textContent = result.data.description || 'Quick reference';
            document.getElementById('wikiSummary').textContent = result.data.summary || 'No summary available.';
            document.getElementById('wikiLink').href = result.data.url || 'https://en.wikipedia.org/wiki/Main_Page';
            showElement('wikiResults');
        })
        .catch(function (error) {
            hideElement('wikiLoading');
            console.error('Wikipedia fetch error:', error);
            showError('wikiError', 'wikiErrorText', 'Unable to fetch results from Wikipedia right now.');
        });
}

/**
 * Send the question to the Flask /ask endpoint and display results.
 */
function askQuestion() {
    var question = document.getElementById('questionInput').value.trim();

    // Validate input
    if (!question) {
        showError('questionError', 'questionErrorText', 'Please enter a question.');
        return;
    }

    // Show loading, hide previous results and errors
    showElement('questionLoading');
    hideElement('questionResults');
    hideElement('questionError');
    setButtonsDisabled(true);

    fetch('/ask', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ question: question })
    })
        .then(function (response) {
            return response.json().then(function (data) {
                return { ok: response.ok, data: data };
            });
        })
        .then(function (result) {
            hideElement('questionLoading');
            setButtonsDisabled(false);

            if (!result.ok || result.data.error) {
                showError('questionError', 'questionErrorText', result.data.error || 'An error occurred.');
                return;
            }

            displayQuestionResults(result.data);
        })
        .catch(function (error) {
            hideElement('questionLoading');
            setButtonsDisabled(false);
            console.error('Fetch error:', error);
            showError('questionError', 'questionErrorText', 'Unable to connect to the server. Please check your connection and try again.');
        });
}

/**
 * Display the AI response for a question in the result cards.
 */
function displayQuestionResults(data) {
    // Short Answer
    setCardContent('shortAnswer', data.short_answer || 'No answer available.');

    // Detailed Explanation
    setCardContent('detailedExplanation', formatText(data.detailed_explanation || 'No explanation available.'));

    // Step-by-Step
    setCardContent('stepByStep', formatText(data.step_by_step || 'Not applicable.'));

    // Example
    setCardContent('exampleContent', formatCodeBlocks(data.example || 'No example available.'));

    // Important Points
    if (data.important_points && Array.isArray(data.important_points) && data.important_points.length > 0) {
        var pointsHtml = '';
        data.important_points.forEach(function (point, index) {
            pointsHtml += '<div class="point-item">';
            pointsHtml += '<span class="point-bullet">' + (index + 1) + '</span>';
            pointsHtml += '<span>' + escapeHtml(point) + '</span>';
            pointsHtml += '</div>';
        });
        document.getElementById('importantPoints').innerHTML = pointsHtml;
    } else {
        setCardContent('importantPoints', 'No specific points available.');
    }

    // Related Topics
    if (data.related_topics && Array.isArray(data.related_topics) && data.related_topics.length > 0) {
        var topicsHtml = '';
        data.related_topics.forEach(function (topic) {
            topicsHtml += '<span class="topic-tag" onclick="setExample(\'' + escapeAttr(topic) + '\')">' + escapeHtml(topic) + '</span>';
        });
        document.getElementById('relatedTopics').innerHTML = topicsHtml;
    } else {
        setCardContent('relatedTopics', 'No related topics available.');
    }

    // Source links
    if (data.source_links && Array.isArray(data.source_links) && data.source_links.length > 0) {
        var linksHtml = '<ul>';
        data.source_links.forEach(function (link) {
            linksHtml += '<li><a href="' + escapeAttr(link) + '" target="_blank" rel="noopener noreferrer">' + escapeHtml(link) + '</a></li>';
        });
        linksHtml += '</ul>';
        document.getElementById('sourceLinks').innerHTML = linksHtml;
    } else {
        document.getElementById('sourceLinks').innerHTML = '<p>No sources provided.</p>';
    }

    // Source links
    if (data.source_links && Array.isArray(data.source_links) && data.source_links.length > 0) {
        var linksHtml = '<ul>';
        data.source_links.forEach(function (link) {
            linksHtml += '<li><a href="' + escapeAttr(link) + '" target="_blank" rel="noopener noreferrer">' + escapeHtml(link) + '</a></li>';
        });
        linksHtml += '</ul>';
        document.getElementById('sourceLinks').innerHTML = linksHtml;
    } else {
        document.getElementById('sourceLinks').innerHTML = '<p>No sources provided.</p>';
    }

    // Mermaid Diagram
    if (data.mermaid_diagram && data.mermaid_diagram !== 'null' && data.mermaid_diagram.trim()) {
        renderMermaidDiagram(data.mermaid_diagram, 'mermaidDiagram', 'diagramCard', 'mermaidCode');
    } else {
        hideElement('diagramCard');
    }

    showElement('questionResults');

    // Scroll to results
    document.getElementById('questionResults').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// ============================================================
// IMAGE HANDLING
// ============================================================

/**
 * Handle image file selection.
 */
function handleImageSelect(event) {
    var file = event.target.files[0];
    if (!file) return;

    // Validate file type
    var allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/webp', 'application/pdf'];
    if (!allowedTypes.includes(file.type) && !file.name.toLowerCase().endsWith('.pdf')) {
        showError('imageError', 'imageErrorText', 'Please upload a PNG, JPG, JPEG, WEBP, or PDF file.');
        event.target.value = '';
        return;
    }

    // Validate file size (5 MB)
    if (file.size > 5 * 1024 * 1024) {
        showError('imageError', 'imageErrorText', 'File size must be less than 5 MB.');
        event.target.value = '';
        return;
    }

    hideElement('imageError');
    selectedImageFile = file;

    // Show an image preview, or a file label for PDFs.
    var preview = document.getElementById('imagePreview');
    if (file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf')) {
        preview.classList.add('hidden');
        document.getElementById('uploadPlaceholder').classList.remove('hidden');
        document.querySelector('#uploadPlaceholder .upload-text').textContent = 'PDF selected: ' + file.name;
    } else {
        var reader = new FileReader();
        reader.onload = function (e) {
            preview.src = e.target.result;
            preview.classList.remove('hidden');
            document.getElementById('uploadPlaceholder').classList.add('hidden');
        };
        reader.readAsDataURL(file);
    }

    // Enable buttons
    document.getElementById('analyzeBtn').disabled = false;
    document.getElementById('removeImageBtn').classList.remove('hidden');
}

/**
 * Remove the selected image.
 */
function removeImage() {
    selectedImageFile = null;
    document.getElementById('imageInput').value = '';
    document.getElementById('imagePreview').classList.add('hidden');
    document.getElementById('imagePreview').src = '';
    document.getElementById('uploadPlaceholder').classList.remove('hidden');
    document.querySelector('#uploadPlaceholder .upload-text').textContent = 'Upload any file or image here';
    document.getElementById('analyzeBtn').disabled = true;
    document.getElementById('removeImageBtn').classList.add('hidden');
    hideElement('imageError');
    hideElement('imageResults');
}

/**
 * Send the selected image or PDF to the Flask /analyze-file endpoint.
 */
function analyzeImage() {
    if (!selectedImageFile) {
        showError('imageError', 'imageErrorText', 'Please select an image or PDF first.');
        return;
    }

    // Show loading
    showElement('imageLoading');
    hideElement('imageResults');
    hideElement('imageError');
    document.getElementById('analyzeBtn').disabled = true;

    var formData = new FormData();
    formData.append('file', selectedImageFile);

    fetch('/analyze-file', {
        method: 'POST',
        body: formData
    })
        .then(function (response) {
            return response.json().then(function (data) {
                return { ok: response.ok, data: data };
            });
        })
        .then(function (result) {
            hideElement('imageLoading');
            document.getElementById('analyzeBtn').disabled = false;

            if (!result.ok || result.data.error) {
                showError('imageError', 'imageErrorText', result.data.error || 'An error occurred during image analysis.');
                return;
            }

            displayImageResults(result.data);
        })
        .catch(function (error) {
            hideElement('imageLoading');
            document.getElementById('analyzeBtn').disabled = false;
            console.error('Fetch error:', error);
            showError('imageError', 'imageErrorText', 'Unable to connect to the server. Please check your connection and try again.');
        });
}

/**
 * Display the AI response for an image analysis.
 */
function displayImageResults(data) {
    // Show uploaded image in results
    var resultImage = document.getElementById('resultImage');
    var preview = document.getElementById('imagePreview');
    var isPdf = selectedImageFile && (selectedImageFile.type === 'application/pdf' || selectedImageFile.name.toLowerCase().endsWith('.pdf'));
    if (preview.src && !isPdf) {
        resultImage.src = preview.src;
        showElement('uploadedImageCard');
    } else {
        hideElement('uploadedImageCard');
    }

    // Detected Content
    setCardContent('detectedContent', formatText(data.detected_content || 'Content analysis not available.'));

    // Answer
    setCardContent('imageAnswer', formatCodeBlocks(data.answer || 'No answer available.'));

    // Step-by-Step
    setCardContent('imageStepByStep', formatText(data.step_by_step || 'Not applicable.'));

    // Important Concepts
    if (data.important_concepts && Array.isArray(data.important_concepts) && data.important_concepts.length > 0) {
        var conceptsHtml = '';
        data.important_concepts.forEach(function (concept, index) {
            conceptsHtml += '<div class="point-item">';
            conceptsHtml += '<span class="point-bullet">' + (index + 1) + '</span>';
            conceptsHtml += '<span>' + escapeHtml(concept) + '</span>';
            conceptsHtml += '</div>';
        });
        document.getElementById('imageConcepts').innerHTML = conceptsHtml;
    } else {
        setCardContent('imageConcepts', 'No specific concepts listed.');
    }

    // Diagram Explanation
    setCardContent('diagramExplanation', formatText(data.diagram_explanation || 'No diagram explanation available.'));

    // Student Tip
    setCardContent('studentTip', formatText(data.student_tip || 'Keep practising and reviewing regularly!'));

    // Source links for image results
    if (data.source_links && Array.isArray(data.source_links) && data.source_links.length > 0) {
        var imageLinksHtml = '<ul>';
        data.source_links.forEach(function (link) {
            imageLinksHtml += '<li><a href="' + escapeAttr(link) + '" target="_blank" rel="noopener noreferrer">' + escapeHtml(link) + '</a></li>';
        });
        imageLinksHtml += '</ul>';
        document.getElementById('imageSourceLinks').innerHTML = imageLinksHtml;
    } else {
        document.getElementById('imageSourceLinks').innerHTML = '<p>No sources provided.</p>';
    }

    // Mermaid Diagram for image results
    if (data.mermaid_diagram && data.mermaid_diagram !== 'null' && data.mermaid_diagram.trim()) {
        renderMermaidDiagram(data.mermaid_diagram, 'imageMermaidDiagram', 'imageDiagramCard', null);
    } else {
        hideElement('imageDiagramCard');
    }

    showElement('imageResults');

    // Scroll to results
    document.getElementById('imageResults').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// ============================================================
// MERMAID DIAGRAM RENDERING
// ============================================================

/**
 * Render a Mermaid diagram safely.
 * @param {string} code - The Mermaid diagram code
 * @param {string} containerId - The ID of the container element
 * @param {string} cardId - The ID of the card to show/hide
 * @param {string|null} codeBlockId - The ID of the code display element (optional)
 */
function renderMermaidDiagram(code, containerId, cardId, codeBlockId) {
    var container = document.getElementById(containerId);
    var card = document.getElementById(cardId);

    // Clean the Mermaid code
    var cleanCode = code.trim();

    // Remove any wrapping code fences
    cleanCode = cleanCode.replace(/^```(?:mermaid)?\s*\n?/i, '');
    cleanCode = cleanCode.replace(/\n?```\s*$/i, '');
    cleanCode = cleanCode.trim();

    // Basic validation: check if it starts with a valid Mermaid keyword
    var validStarts = ['graph', 'flowchart', 'sequenceDiagram', 'classDiagram',
        'stateDiagram', 'erDiagram', 'gantt', 'pie', 'gitGraph',
        'journey', 'mindmap', 'timeline', 'quadrantChart', 'sankey',
        'xychart', 'block'];
    var isValid = validStarts.some(function (keyword) {
        return cleanCode.toLowerCase().startsWith(keyword.toLowerCase());
    });

    if (!isValid) {
        hideElement(cardId);
        return;
    }

    // Show the code in the toggle block if applicable
    if (codeBlockId) {
        document.getElementById(codeBlockId).textContent = cleanCode;
    }

    // Render with Mermaid
    var diagramId = 'mermaid-' + Date.now();

    try {
        mermaid.render(diagramId, cleanCode).then(function (result) {
            container.innerHTML = result.svg;
            showElement(cardId);
        }).catch(function (error) {
            console.warn('Mermaid rendering failed:', error);
            container.innerHTML = '<p style="color: #64748b; font-style: italic;">Unable to generate the diagram. The explanation is still available above.</p>';
            showElement(cardId);
        });
    } catch (error) {
        console.warn('Mermaid rendering error:', error);
        container.innerHTML = '<p style="color: #64748b; font-style: italic;">Unable to generate the diagram. The explanation is still available above.</p>';
        showElement(cardId);
    }
}

/**
 * Toggle the visibility of the raw Mermaid code block.
 */
function toggleMermaidCode() {
    var codeBlock = document.getElementById('mermaidCodeBlock');
    var btn = document.getElementById('toggleDiagramCode');

    if (codeBlock.classList.contains('hidden')) {
        codeBlock.classList.remove('hidden');
        btn.textContent = 'Hide Diagram Code';
    } else {
        codeBlock.classList.add('hidden');
        btn.textContent = 'View Diagram Code';
    }
}

// ============================================================
// TEXT FORMATTING HELPERS
// ============================================================

/**
 * Escape HTML special characters to prevent XSS.
 */
function escapeHtml(text) {
    var div = document.createElement('div');
    div.appendChild(document.createTextNode(text));
    return div.innerHTML;
}

/**
 * Escape a string for use in an HTML attribute (e.g., onclick).
 */
function escapeAttr(text) {
    return text.replace(/'/g, "\\'").replace(/"/g, '&quot;');
}

/**
 * Format plain text into HTML paragraphs.
 * Handles numbered lists and line breaks.
 */
function formatText(text) {
    if (!text) return '';

    var escaped = escapeHtml(text);

    // Convert numbered lists (e.g., "1. Item")
    escaped = escaped.replace(/^(\d+)\.\s+(.+)$/gm, '<li>$2</li>');

    // Wrap consecutive <li> items in <ol>
    escaped = escaped.replace(/((?:<li>.*?<\/li>\s*)+)/g, '<ol>$1</ol>');

    // Convert bullet points
    escaped = escaped.replace(/^[-*]\s+(.+)$/gm, '<li>$1</li>');
    escaped = escaped.replace(/((?:<li>.*?<\/li>\s*)+)/g, function (match) {
        // Only wrap in <ul> if not already in <ol>
        if (match.indexOf('<ol>') === -1) {
            return '<ul>' + match + '</ul>';
        }
        return match;
    });

    // Convert **bold** text
    escaped = escaped.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

    // Convert line breaks to paragraphs
    var paragraphs = escaped.split(/\n\s*\n/);
    if (paragraphs.length > 1) {
        escaped = paragraphs.map(function (p) {
            p = p.trim();
            if (!p) return '';
            // Don't wrap if it's already a list
            if (p.startsWith('<ol>') || p.startsWith('<ul>')) return p;
            return '<p>' + p.replace(/\n/g, '<br>') + '</p>';
        }).join('');
    } else {
        escaped = escaped.replace(/\n/g, '<br>');
    }

    return escaped;
}

/**
 * Format text that may contain code blocks.
 * Detects ```language ... ``` patterns and wraps them in <pre><code>.
 */
function formatCodeBlocks(text) {
    if (!text) return '';

    // Split by code fences
    var parts = text.split(/(```[\s\S]*?```)/g);
    var result = '';

    parts.forEach(function (part) {
        if (part.startsWith('```')) {
            // Extract code content
            var codeContent = part.replace(/^```\w*\n?/, '').replace(/\n?```$/, '');
            result += '<pre><code>' + escapeHtml(codeContent) + '</code></pre>';
        } else {
            result += formatText(part);
        }
    });

    return result;
}

/**
 * Set the innerHTML of a card body element.
 */
function setCardContent(elementId, content) {
    var element = document.getElementById(elementId);
    if (element) {
        // If content doesn't contain HTML tags, wrap in paragraph
        if (content.indexOf('<') === -1) {
            element.innerHTML = '<p>' + escapeHtml(content) + '</p>';
        } else {
            element.innerHTML = content;
        }
    }
}

// ============================================================
// UI UTILITY FUNCTIONS
// ============================================================

/**
 * Show an element by removing the 'hidden' class.
 */
function showElement(id) {
    var el = document.getElementById(id);
    if (el) el.classList.remove('hidden');
}

/**
 * Hide an element by adding the 'hidden' class.
 */
function hideElement(id) {
    var el = document.getElementById(id);
    if (el) el.classList.add('hidden');
}

/**
 * Show an error message in the specified error container.
 */
function showError(containerId, textId, message) {
    document.getElementById(textId).textContent = message;
    showElement(containerId);
}

/**
 * Enable or disable the Ask AI and Clear buttons.
 */
function setButtonsDisabled(disabled) {
    document.getElementById('askBtn').disabled = disabled;
    document.getElementById('clearBtn').disabled = disabled;
}

// ============================================================
// DRAG AND DROP SUPPORT
// ============================================================

(function () {
    var uploadArea = document.getElementById('uploadArea');

    uploadArea.addEventListener('dragover', function (e) {
        e.preventDefault();
        uploadArea.classList.add('drag-over');
    });

    uploadArea.addEventListener('dragleave', function (e) {
        e.preventDefault();
        uploadArea.classList.remove('drag-over');
    });

    uploadArea.addEventListener('drop', function (e) {
        e.preventDefault();
        uploadArea.classList.remove('drag-over');

        var files = e.dataTransfer.files;
        if (files.length > 0) {
            // Set the file input
            var input = document.getElementById('imageInput');
            // We can't set input.files directly, so we trigger the handler manually
            var file = files[0];

            // Validate
            var allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/webp'];
            if (!allowedTypes.includes(file.type)) {
                showError('imageError', 'imageErrorText', 'Please upload a valid PNG, JPG, JPEG, or WEBP image.');
                return;
            }
            if (file.size > 5 * 1024 * 1024) {
                showError('imageError', 'imageErrorText', 'Image size must be less than 5 MB.');
                return;
            }

            hideElement('imageError');
            selectedImageFile = file;

            var reader = new FileReader();
            reader.onload = function (ev) {
                var preview = document.getElementById('imagePreview');
                preview.src = ev.target.result;
                preview.classList.remove('hidden');
                document.getElementById('uploadPlaceholder').classList.add('hidden');
            };
            reader.readAsDataURL(file);

            document.getElementById('analyzeBtn').disabled = false;
            document.getElementById('removeImageBtn').classList.remove('hidden');
        }
    });
})();
