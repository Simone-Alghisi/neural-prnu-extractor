---
title:
- Neural PRNU extractor
subtitle:
- A denoising neural network
aspectratio:
- 43
institute:
- University of Trento
author:
- \href{https://github.com/Simone-Alghisi}{Simone Alghisi}
- \href{https://github.com/samuelebortolotti}{Samuele Bortolotti}
- \href{https://github.com/massimo-rizzoli}{Massimo Rizzoli}
date:
- \today
lang:
- en-US
section-titles:
- false
theme:
- Copenhagen
colortheme:
- default
navigation:
- horizontal
logo:
- imgs/unitn.pdf
fontsize:
- 10mm
bibliography: bibliography.bib
link-citations: true
nocite: |
  @*
---

# Introduction

## Noise extraction
Noise reduction is the process of removing noise from a signal for practical purposes such as computer vision [@enwiki:1065098521]

## PRNU
Photo response non-uniformity is a form of fixed-pattern noise related to digital image sensors, as used in cameras and optical instruments [@enwiki:1048256617].

# Objective
Train a model to extract the PRNU noise for device identification.

![PRNU extraction pipeline](./imgs/prnu_extraction_pipeline.pdf)

# Residual FFDNet [@ipol.2019.231]

![FFDNet architecture](./imgs/ffdnet.png)

## Strenght points
* removes spatially variant noise, specifying a non-uniform noise level map;
* works with low noise levels ($\sigma \in [0, 75]$);
* uses state of the art CNN structures as residual connections.

# Residual FFDNet - Our contribution

::: {.columns align=center}

:::: column

![ ](imgs/learning_rate.pdf)

::::

:::: column

## ReduceLROnPlateau
Instead of reducing manually the learning rate, we introduced this function in order to decrease it automatically after a *patience* threshold.

::::

:::

# Residual FFDNet - Our contribution

## Resource usage
We introduced a stopping criterion if the requested resources exceed a user-fixed for the amount of GPU memory. Once exceeded, the procedure stops.

## Different experiments
So as to handle different training sessions, we have created an argument parser to specify several parameters (e.g. experiment name, datasets, epochs, gpu fraction, ...)

# Residual FFDNet - Our contribution

## Wiener as groundtruth
We trained FFDNet by using the Wiener filter to produce ground-truth noise. The extracted noise is used to compute the loss of the residual net

$$\mathcal{L}_{res}(\theta) = \frac{1}{2m}\sum_{j=1}^{m}{\parallel \mathcal{F}((\tilde{\mathrm{I}}_j, \mathrm{M}_j); \theta) - \mathrm{N}_j \parallel^2}$$

## Green channel
In order to work with the Wiener filter, we have extracted the green channel, without taking into account possible contributions of the others.

# Dataset [@shullani2017vision]

The dataset used to train the model and evaluate its performance is the VISION dataset, provided by Università degli Studi di Firenze.

## Training (Train + Validation)

For training and validation we used the first three sets of camera models’ images (i.e. D01, D02, D03).

## Test

Instead, for the testing phase with the PRNU we picked the next three sets of camera models images (D04, D05, D06).

# Training

We trained two different models

* one using the Wiener approach described previously;
* the other using the original approach with $\sigma \in [0, 5]$.

Generally speaking, we used the following setup for both models

| **Parameter**     |   |   | **Value** |
|:------------------|:-:|:-:|----------:|
| N. epochs         |   |   | 250       |
| Total time (HH)   |   |   | 44        |
| Batch size        |   |   | 64        |
| Patch size (WxH)  |   |   | 100       |
| GPU (GB)          |   |   | 3         |
| Patience (epochs) |   |   | 40        |

# Resume training

We integrated into the original checkpoint system the new information for the modified neural network.

In particular:

* total/elapsed epochs
* network weights
* learning rate and weights for the optimizer
* patience for the scheduler
* current best loss
* all the initial parameters

# PRNU Extraction [@10.2352/ISSN.2470-1173.2016.8.MWSF-086]

To evaluate the results obtained from the training of FFDNet, we

1. considered a set of different camera models *flat* images
2. extracted the noise using the neural implementation
3. obtained the camera fingerprint for each model [@luca_bondi_2019_2554965]
4. classified a set of *nat* images using the resulting PRNU

Furthermore, we also created a packaged installation for \texttt{pip} and added it in the program requirements.



# PRNU Extraction - Metrics
![Evaluation of PRNU accuracy by using ROC curve](imgs/roc.pdf){width=60%}

# Results

\definecolor{darkgreen}{RGB}{66, 207, 68}

| **Technique** | **Sigma** | **Cut Dim** | **CC** | **PCE** | **Time** |
|:--------------|:---------:|:-----------:|:------:|:-------:|:--------:|
| \textcolor{gray}{Wavelet}     | \textcolor{gray}{5}         | \textcolor{gray}{512 x 512}   | \textcolor{gray}{0.97}   | \textcolor{gray}{0.96}    | \textcolor{gray}{04m 49s}  |
| Neural Wiener                 | Adaptive  | 256 x 256   | 0.94   | 0.83    | 03m 18s  |
| Neural Wiener                 | Adaptive  | 512 x 512   | **0.96** | 0.95    | 05m 20s  |
| Neural Wiener                 | Adaptive  | 1024 x 1024 | **0.98**   | 0.96    | \textcolor{red}{15m 18s}  |
| Neural Wiener                 | 5         | 512 x 512   | 0.95   | 0.92    | 05m 12s  |
| Neural 0-5                    | Adaptive  | 512 x 512   | 0.93   | 0.92    | 05m 14s  |
| Neural 0-5                    | 5         | 512 x 512   | 0.95   | **0.97**    | 05m 17s  |
| FFDNet                        | Adaptive  | 512 x 512   | 0.96   | 0.94    | 05m 03s  |
| \textcolor{darkgreen}{FFDNet}                        | 5         | 512 x 512   | **0.96**   | **0.96**    | 04m 57s  |

# Resources

## Repositories

* [Neural PRNU extractor](https://github.com/samuelebortolotti/neural-prnu-extractor)
* [PRNU Python (neural)](https://github.com/samuelebortolotti/prnu-python)

## Collaborators' Github

* [Simone Alghisi](https://github.com/Simone-Alghisi)
* [Samuele Bortolotti](https://github.com/samuelebortolotti)
* [Massimo Rizzoli](https://github.com/massimo-rizzoli)

# Conclusions

\begin{center}
  \LARGE{Thanks for your attention!}
\end{center}

<!--# Appendix-->
<!---->
<!--## Appendix content-->
<!--The appendix contains the topics we are not able to discuss during the oral examination-->

# References {.allowframebreaks}
