# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Fenerbahçe Tetris — a single-file browser-based Tetris game themed around the Fenerbahçe football club. The entire game (HTML, CSS, JavaScript) lives in `tetris.html`. Open it directly in a browser to play; no build step or dependencies required.

## Architecture

- **Single-file app**: `tetris.html` contains everything — styles in `<style>`, markup in `<body>`, game logic in `<script>`.
- **Rendering**: Uses two `<canvas>` elements — `#board` for the 10×20 game grid (30px blocks) and `#next` for the next-piece preview. A third canvas `#fb-logo` draws the club logo, and `#jersey-canvas` draws player jerseys in popups.
- **Game loop**: `requestAnimationFrame`-based loop (`loop()`) with delta-time accumulator for piece drop timing. Speed increases with level (every 10 cleared lines).
- **Player popup system**: Clearing lines triggers `showPlayerPopup()` which displays a random Fenerbahçe player card with a drawn jersey. Players are defined in the `FB_PLAYERS` array.
- **Collision & rotation**: `collides()` checks bounds and occupied cells. `rotate()` does clockwise rotation with wall-kick offsets (0, ±1, ±2).

## Language

The UI text is in Turkish. Keep all user-facing strings in Turkish when making changes.

## Git Workflow

All changes should be committed with clean, descriptive messages and pushed to GitHub (origin: `serhose/Claude-Test`, branch: `master`).
