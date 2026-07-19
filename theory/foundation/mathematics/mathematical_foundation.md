# Mathematical Foundation

Distilled from `program_d_scientific_foundation_v0.1.md` Phase 3.

## Free Energy Functional

```
F(t) = λ · H[P(θₜ₊₁ | θ₁:ₜ)] + μ · S(xₜ, x̂ₜ) + ν · L(Θₜ)
```

Where:
- **H** = Entropy of the predictive distribution over next latent state
- **S** = Surprise (prediction error at the sensory level)
- **L** = Structural load (active clusters + anomaly volume)
- λ, μ, ν = Free energy coefficients (λ=1.0, μ=2.0, ν=0.5)

## MDL Criterion for Concept Birth

```
G = H_before − H_after − λ_model
```

A new concept is born when the description-length gain G exceeds a threshold.

## Prediction Error

```
S(x, x̂) = ‖x − x̂‖₂²
```

## Dirichlet-Markov Conjugate Prior

The predictive distribution over the next latent state follows a Dirichlet-Markov
process with concentration parameter α and transition kernel K.

## Null-Referenced Emergence Statistic

```
M_0(θ_k) = M(θ_k) − E[M | H₀]
```

Where H₀ is the null hypothesis that the observed structure is no different from
a shuffled or capacity-matched random process.
