## emotional-fuzzy-axis
A computational framework for mapping NLP emotion probabilities onto dual-state linear coordinates using Fuzzy Logic and Linear Scalarization.

## Abstract
This project implements a novel approach to Affective Computing, diverging from the traditional Russell's Circumplex Model. Instead of mapping emotions onto a single continuous 2D plane (Valence/Arousal), this framework utilizes Fuzzy Logic to classify the emotional context into two discrete states (Positive/Negative) and projects them onto state-specific linear axes.

The core objective is to convert high-dimensional probability vectors (28 classes from RoBERTa) into interpretable low-dimensional coordinates (X/Y intensity) for dynamic system adaptation.

The repository includes a WebSocket-based chat interface serving as a proof-of-concept visualization tool to demonstrate the algorithm's real-time performance.

Core Methodology
1. Emotion Extraction
The input text is processed using the RoBERTa-base-go_emotions transformer model, which outputs a probability distribution across 28 distinct emotional labels (e.g., Admiration, Remorse, Excitement).

2. Fuzzy Aggregation & Linear Scalarization
Unlike standard categorical classification (selecting the label with the highest score), this project applies Linear Scalarization. Related emotions are grouped and weighted to calculate the intensity along specific axes.

The system defines two distinct coordinate spaces:

State A: Positive Spectrum

X-Axis (Satisfaction): Weighted sum of Gratitude (0.5) and Joy (1.0).

Y-Axis (Affection): Weighted sum of Interest (0.5) and Love (1.0).

State B: Negative Spectrum

X-Axis (Distress): Weighted sum of Sadness (0.5) and Anger (1.0).

Y-Axis (Self-Conscious): Weighted sum of Shame (0.5) and Envy (1.0).

3. Algorithm Implementation
The logic is encapsulated in app/ml_engine.py
