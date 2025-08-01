"""
Framework configuration for different programming languages
"""

FRAMEWORK_CONFIG = {
    "java": [
        {"name": "spring", "label": "Spring Framework", "description": "Enterprise Java framework"},
        {"name": "spring_boot", "label": "Spring Boot", "description": "Rapid application development with Spring"},
        {"name": "jakarta_ee", "label": "Jakarta EE", "description": "Enterprise Java platform"},
        {"name": "micronaut", "label": "Micronaut", "description": "Modern JVM framework"},
        {"name": "quarkus", "label": "Quarkus", "description": "Supersonic Subatomic Java"},
        {"name": "play", "label": "Play Framework", "description": "Web framework for Java and Scala"},
        {"name": "struts", "label": "Apache Struts", "description": "MVC framework for Java"},
        {"name": "jsf", "label": "JavaServer Faces", "description": "Component-based UI framework"},
        {"name": "vaadin", "label": "Vaadin", "description": "Web application framework"},
        {"name": "none", "label": "No Framework", "description": "Plain Java without framework"}
    ],
    "python": [
        {"name": "django", "label": "Django", "description": "High-level Python web framework"},
        {"name": "flask", "label": "Flask", "description": "Lightweight web framework"},
        {"name": "fastapi", "label": "FastAPI", "description": "Modern, fast web framework"},
        {"name": "pyramid", "label": "Pyramid", "description": "Flexible Python web framework"},
        {"name": "tornado", "label": "Tornado", "description": "Asynchronous web framework"},
        {"name": "bottle", "label": "Bottle", "description": "Fast and simple WSGI framework"},
        {"name": "cherrypy", "label": "CherryPy", "description": "Object-oriented web framework"},
        {"name": "web2py", "label": "web2py", "description": "Full-stack web framework"},
        {"name": "aiohttp", "label": "aiohttp", "description": "Async HTTP client/server framework"},
        {"name": "none", "label": "No Framework", "description": "Plain Python without framework"}
    ],
    "javascript": [
        {"name": "react", "label": "React", "description": "JavaScript library for building user interfaces"},
        {"name": "vue", "label": "Vue.js", "description": "Progressive JavaScript framework"},
        {"name": "angular", "label": "Angular", "description": "Platform for building mobile and desktop web applications"},
        {"name": "express", "label": "Express.js", "description": "Fast, unopinionated web framework"},
        {"name": "next", "label": "Next.js", "description": "React framework for production"},
        {"name": "nuxt", "label": "Nuxt.js", "description": "Vue.js framework for production"},
        {"name": "svelte", "label": "Svelte", "description": "Cybernetically enhanced web apps"},
        {"name": "ember", "label": "Ember.js", "description": "A framework for ambitious web developers"},
        {"name": "backbone", "label": "Backbone.js", "description": "Give your JS App some backbone"},
        {"name": "jquery", "label": "jQuery", "description": "JavaScript library"},
        {"name": "none", "label": "No Framework", "description": "Plain JavaScript without framework"}
    ],
    "typescript": [
        {"name": "react", "label": "React with TypeScript", "description": "React with TypeScript support"},
        {"name": "vue", "label": "Vue.js with TypeScript", "description": "Vue.js with TypeScript support"},
        {"name": "angular", "label": "Angular", "description": "Platform for building mobile and desktop web applications"},
        {"name": "next", "label": "Next.js with TypeScript", "description": "Next.js with TypeScript support"},
        {"name": "nuxt", "label": "Nuxt.js with TypeScript", "description": "Nuxt.js with TypeScript support"},
        {"name": "svelte", "label": "Svelte with TypeScript", "description": "Svelte with TypeScript support"},
        {"name": "express", "label": "Express.js with TypeScript", "description": "Express.js with TypeScript support"},
        {"name": "nest", "label": "NestJS", "description": "Progressive Node.js framework"},
        {"name": "none", "label": "No Framework", "description": "Plain TypeScript without framework"}
    ],
    "cobol": [
        {"name": "cics", "label": "CICS", "description": "Customer Information Control System"},
        {"name": "ims", "label": "IMS", "description": "Information Management System"},
        {"name": "db2", "label": "DB2", "description": "Database management system"},
        {"name": "jcl", "label": "JCL", "description": "Job Control Language"},
        {"name": "none", "label": "No Framework", "description": "Plain COBOL without framework"}
    ],
    "cpp": [
        {"name": "qt", "label": "Qt", "description": "Cross-platform application framework"},
        {"name": "boost", "label": "Boost", "description": "Collection of peer-reviewed portable C++ source libraries"},
        {"name": "stl", "label": "STL", "description": "Standard Template Library"},
        {"name": "mfc", "label": "MFC", "description": "Microsoft Foundation Classes"},
        {"name": "wxwidgets", "label": "wxWidgets", "description": "Cross-platform GUI library"},
        {"name": "none", "label": "No Framework", "description": "Plain C++ without framework"}
    ],
    "csharp": [
        {"name": "asp_net", "label": "ASP.NET", "description": "Web application framework"},
        {"name": "asp_net_core", "label": "ASP.NET Core", "description": "Cross-platform web framework"},
        {"name": "wpf", "label": "WPF", "description": "Windows Presentation Foundation"},
        {"name": "winforms", "label": "Windows Forms", "description": "Desktop application framework"},
        {"name": "xamarin", "label": "Xamarin", "description": "Cross-platform mobile development"},
        {"name": "blazor", "label": "Blazor", "description": "Web framework using C# and HTML"},
        {"name": "none", "label": "No Framework", "description": "Plain C# without framework"}
    ],
    "php": [
        {"name": "laravel", "label": "Laravel", "description": "PHP web application framework"},
        {"name": "symfony", "label": "Symfony", "description": "PHP web application framework"},
        {"name": "codeigniter", "label": "CodeIgniter", "description": "PHP framework"},
        {"name": "yii", "label": "Yii", "description": "High-performance PHP framework"},
        {"name": "cakephp", "label": "CakePHP", "description": "Rapid development framework"},
        {"name": "zend", "label": "Zend Framework", "description": "Enterprise PHP framework"},
        {"name": "slim", "label": "Slim", "description": "PHP micro-framework"},
        {"name": "none", "label": "No Framework", "description": "Plain PHP without framework"}
    ],
    "ruby": [
        {"name": "rails", "label": "Ruby on Rails", "description": "Web application framework"},
        {"name": "sinatra", "label": "Sinatra", "description": "Lightweight web framework"},
        {"name": "hanami", "label": "Hanami", "description": "Modern Ruby web framework"},
        {"name": "grape", "label": "Grape", "description": "REST-like API framework"},
        {"name": "none", "label": "No Framework", "description": "Plain Ruby without framework"}
    ],
    "go": [
        {"name": "gin", "label": "Gin", "description": "HTTP web framework"},
        {"name": "echo", "label": "Echo", "description": "High performance web framework"},
        {"name": "fiber", "label": "Fiber", "description": "Express inspired web framework"},
        {"name": "revel", "label": "Revel", "description": "Full-stack web framework"},
        {"name": "beego", "label": "Beego", "description": "Full-stack web framework"},
        {"name": "none", "label": "No Framework", "description": "Plain Go without framework"}
    ],
    "rust": [
        {"name": "actix", "label": "Actix", "description": "Powerful web framework"},
        {"name": "rocket", "label": "Rocket", "description": "Web framework for Rust"},
        {"name": "warp", "label": "Warp", "description": "Fast web framework"},
        {"name": "axum", "label": "Axum", "description": "Web application framework"},
        {"name": "none", "label": "No Framework", "description": "Plain Rust without framework"}
    ]
}

def get_frameworks_for_language(language: str) -> list:
    """Get available frameworks for a specific language"""
    return FRAMEWORK_CONFIG.get(language.lower(), [])

def get_all_frameworks() -> dict:
    """Get all framework configurations"""
    return FRAMEWORK_CONFIG

def is_valid_framework(language: str, framework: str) -> bool:
    """Check if a framework is valid for a given language"""
    frameworks = get_frameworks_for_language(language)
    return any(f["name"] == framework for f in frameworks)

def get_framework_label(language: str, framework: str) -> str:
    """Get the display label for a framework"""
    frameworks = get_frameworks_for_language(language)
    for f in frameworks:
        if f["name"] == framework:
            return f["label"]
    return framework 