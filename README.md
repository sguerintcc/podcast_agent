# Podcast Agent

Podcast Agent monitors podcast RSS feeds (including YouTube channel feeds), fetches episode transcripts, summarizes them with an LLM, and stores transcripts and summaries in SQLite.

## Features
- Watch RSS feeds for new episodes
- Fetch transcripts from YouTube videos
- Summarize and tag episodes via an LLM client (OpenAI or echo placeholder)
- Persist transcripts, summaries, and tags to SQLite
- Simple `main.py` entry point—no CLI flags required

## Getting Started

### Prerequisites
- Python 3.10+
- Optional: An OpenAI API key if you want to use the OpenAI LLM client

### Installation
1. Create and activate a virtual environment.
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
2. Install dependencies.
   ```bash
   pip install -r requirements.txt
   ```

### Configuration
1. Copy `config.example.json` to `config.json`.
   ```bash
   cp config.example.json config.json
   ```
2. Edit `config.json` to add your feed URLs and preferred settings.
3. (Optional) Set `PODCAST_AGENT_CONFIG` to point to a different config file.
4. If you use the OpenAI LLM client, set `OPENAI_API_KEY` in your environment.

### Running the Pipeline
Execute the main script to process configured feeds once:
```bash
python main.py
```
The pipeline will fetch new episodes, download transcripts, summarize them, and store results in the SQLite database path defined in your config.

## Examples
Minimal, runnable examples are provided in the `examples/` directory to demonstrate each component in isolation and together.

- `examples/fetch_feed.py`: List recent episodes from an RSS feed using `RSSFeedMonitor`.
- `examples/transcript_fetch.py`: Retrieve a transcript for a YouTube video using `YouTubeTranscriptClient`.
- `examples/summarize_transcript.py`: Summarize a transcript with the echo LLM client.
- `examples/full_pipeline.py`: Show how to wire the pipeline with static clients for offline testing.
- `examples/youtube_channel_monitor.py`: Crawl a YouTube channel's upload history using `YouTubeChannelMonitor`.

Use `YouTubeChannelMonitor` when you want to crawl the full upload history of a YouTube channel without YouTube Data API keys.

Run any example with Python, optionally adjusting the constants in each file to match your feeds, video URLs, or sample data:
```bash
python examples/fetch_feed.py
```

## Notes
- The default echo LLM client returns placeholder summaries; switch to OpenAI by setting `llm.provider` to `"openai"` and specifying a `model` in the config.
- The YouTube transcript fetcher uses `youtube-transcript-api`, which may not provide transcripts for every video (e.g., if captions are disabled).
- SQLite databases are created automatically; ensure the process has write access to the configured path.

## Development
Run a quick syntax check:
```bash
python -m compileall podcast_agent main.py examples
```
