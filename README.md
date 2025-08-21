# 🕊️ Peace Bot - Discord AI Assistant

A feature-rich Discord bot with AI chat, image generation, and dynamic presence management. Built with Python and Discord.py.

![Discord](https://img.shields.io/badge/Discord-7289DA?style=for-the-badge&logo=discord&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Gemini](https://img.shields.io/badge/Gemini-4285F4?style=for-the-badge&logo=google&logoColor=white)
![Stability AI](https://img.shields.io/badge/Stability_AI-000000?style=for-the-badge&logo=stability-ai&logoColor=white)

## ✨ Features

### 🤖 AI Chat Integration
- **Gemini 2.0** powered conversations
- Configurable AI personality (default: casual, rowdy friend)
- Adjustable temperature and response length
- Clean, prefix-free responses

### 🎨 Image Generation
- **Stability AI SDXL** for high-quality images
- 1024x1024 resolution output
- Simple text-to-image prompts

### 🎭 Dynamic Presence
- Bot status changes based on activity
- Idle: "Playing Dynamically" (after 2 minutes of inactivity)
- Active: "Listening to help" (when commands are used)

### 👋 Welcome System
- Customizable welcome channel per server
- Rich embed welcome messages with member avatars
- Server-specific welcome images

### ⚙️ Server Management
- Per-server configuration settings
- Admin-only settings management
- Slash commands and prefix commands

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Discord Bot Token
- Gemini API Key
- Stability AI API Key

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd peace-bot
   ```

2. **Install dependencies**
   ```bash
   cd bot.py
   pip install discord.py google-generativeai python-dotenv requests
   ```

3. **Configure environment variables**
   Create a `.env` file in the `bot.py` directory:
   ```env
   TOKEN=your_discord_bot_token
   GEMINI_API_KEY=your_gemini_api_key
   STABILITY_API_KEY=your_stability_api_key
   ```

4. **Set up Discord Bot**
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Create a new application
   - Go to Bot section and copy your token
   - Enable **Server Members Intent** and **Message Content Intent**
   - Generate invite link with scopes: `bot` and `applications.commands`

5. **Run the bot**
   ```bash
   python bot.py
   ```

## 📋 Commands

### 🤖 AI Commands
| Command | Description | Example |
|---------|-------------|---------|
| `&ask [question]` | Ask the AI anything | `&ask What's the fastest land animal?` |
| `/ask question:[text]` | Slash command version | `/ask question:What's the fastest land animal?` |

### 🎨 Image Commands
| Command | Description | Example |
|---------|-------------|---------|
| `&imagine [prompt]` | Generate an image | `&imagine a cyberpunk city at night` |
| `/imagine prompt:[text]` | Slash command version | `/imagine prompt:a cyberpunk city at night` |

### ⚙️ Settings Commands (Admin Only)
| Command | Description | Example |
|---------|-------------|---------|
| `&set ai_model [model]` | Change AI model | `&set ai_model gemini-2.0-pro` |
| `&set ai_temperature [0-2]` | Adjust AI creativity | `&set ai_temperature 0.9` |
| `&set ai_max_tokens [50-2000]` | Set response length | `&set ai_max_tokens 1000` |
| `&set ai_persona [text]` | Customize AI personality | `&set ai_persona Talk like a wise mentor` |
| `&set prefix [char]` | Change bot prefix | `&set prefix !` |
| `&settings` | View current settings | `&settings` |

### 🏠 Welcome Commands (Admin Only)
| Command | Description |
|---------|-------------|
| `&setwelcomechannel` | Set welcome channel |
| `&getwelcomechannel` | Show current welcome channel |

### 🎯 Utility Commands
| Command | Description |
|---------|-------------|
| `&hello` | Bot says hi |
| `&mf` | Bot replies "latom!" |
| `&help` | Show help menu |

## 🎛️ Configuration

### AI Models Available
- `gemini-2.0-flash` (default) - Fast, efficient
- `gemini-2.0-pro` - More capable, slower

### Image Generation
- **Model**: Stable Diffusion XL (1024x1024)
- **Provider**: Stability AI
- **Quality**: High-resolution, detailed images

### Default AI Personality
```
Talk like a casual, rowdy friend: cheeky, energetic, a bit teasing; 
use light slang and occasional emojis. Keep it short and helpful. 
No profanity, slurs, NSFW, harassment, hate, or personal attacks. 
Follow Discord rules.
```

## 🔧 Advanced Setup

### Custom AI Personality
Set a custom personality for your server:
```bash
&set ai_persona "You are a wise mentor who speaks in ancient proverbs and gives life advice."
```

### Server-Specific Settings
Each Discord server can have different:
- AI models and parameters
- Bot prefix
- AI personality
- Welcome channel

### Environment Variables
| Variable | Description | Required |
|----------|-------------|----------|
| `TOKEN` | Discord bot token | ✅ |
| `GEMINI_API_KEY` | Google Gemini API key | ✅ |
| `STABILITY_API_KEY` | Stability AI API key | ✅ |

## 🛠️ Development

### Project Structure
```
peace-bot/
├── README.md
└── bot.py/
    ├── bot.py              # Main bot logic
    ├── help_embed.py       # Help command functionality
    ├── pyproject.toml      # Dependencies
    ├── poetry.lock         # Locked versions
    └── .env               # Environment variables
```

### Key Features Implementation
- **Dynamic Presence**: Real-time status updates based on command usage
- **Multi-Provider AI**: Gemini for text, Stability AI for images
- **Server Isolation**: Each server maintains independent settings
- **Error Handling**: Graceful fallbacks and user-friendly error messages
- **Rate Limiting**: Built-in protection against API abuse

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Discord.py** - Discord API wrapper
- **Google Gemini** - AI chat capabilities
- **Stability AI** - Image generation
- **Discord** - Platform and API

## 📞 Support

If you encounter any issues or have questions:
1. Check the [Issues](../../issues) page
2. Create a new issue with detailed information
3. Include error messages and steps to reproduce

---

**Made with ❤️ for Discord communities**
