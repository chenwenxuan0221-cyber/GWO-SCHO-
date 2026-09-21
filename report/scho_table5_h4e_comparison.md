# H4e — SCHO Table-5 structural ablation reproduction

## Reproduction tier

`SCHO: SOURCE-FAITHFUL CONTROL`

`Five ablations: PAPER-DESCRIBED / CONTROLLED-STRUCTURAL-INTERPRETATION`

## Protocol

- Models: SCHO, SCHO_NT, SCHO_NSTF, SCHO_NFTF, SCHO_NSF, SCHO_NFF
- Functions: F1–F23
- N = 30
- MaxIter = 500
- 30 runs/model/function
- seeds = 1000–1029 (project convention)
- common objective-RNG seed across variants for the same function/run
- sample STD (`ddof=1`) saved as the primary Table-5 comparison STD
- execution workers used: 4

Total formal runs: 4140.

## Reproduced ranking

| Variant | Repro Mean Rank | Paper Mean Rank | Repro Final Rank | Paper Final Rank |
|---|---:|---:|---:|---:|
| SCHO | 1.82609 | 1.65 | 1 | 1 |
| SCHO_NT | 3.08696 | 2.96 | 3 | 3 |
| SCHO_NSTF | 3.17391 | 3.35 | 4 | 4 |
| SCHO_NFTF | 4.56522 | 4.52 | 6 | 6 |
| SCHO_NSF | 2.26087 | 2.13 | 2 | 2 |
| SCHO_NFF | 3.56522 | 3.35 | 5 | 4 |

## Per-function Best / Average / sample STD / rank

### F1

| Variant | Best | Average | STD | Rank |
|---|---:|---:|---:|---:|
| SCHO | 0 | 0 | 0 | 1 |
| SCHO_NT | 0 | 0 | 0 | 1 |
| SCHO_NSTF | 0 | 0 | 0 | 1 |
| SCHO_NFTF | 1.19243e-13 | 3.74684e-12 | 6.20587e-12 | 6 |
| SCHO_NSF | 0 | 0 | 0 | 1 |
| SCHO_NFF | 1.24383e-17 | 1.64292e-12 | 3.97215e-12 | 5 |

### F2

| Variant | Best | Average | STD | Rank |
|---|---:|---:|---:|---:|
| SCHO | 0 | 0 | 0 | 1 |
| SCHO_NT | 0 | 0 | 0 | 1 |
| SCHO_NSTF | 0 | 0 | 0 | 1 |
| SCHO_NFTF | 4.67971e-09 | 2.56602e-08 | 2.20925e-08 | 6 |
| SCHO_NSF | 0 | 0 | 0 | 1 |
| SCHO_NFF | 1.38395e-10 | 1.17455e-08 | 1.16471e-08 | 5 |

### F3

| Variant | Best | Average | STD | Rank |
|---|---:|---:|---:|---:|
| SCHO | 0 | 0 | 0 | 1 |
| SCHO_NT | 0 | 0 | 0 | 1 |
| SCHO_NSTF | 0 | 0 | 0 | 1 |
| SCHO_NFTF | 0.000539275 | 0.275818 | 0.777373 | 6 |
| SCHO_NSF | 0 | 0 | 0 | 1 |
| SCHO_NFF | 2.16976e-07 | 0.133678 | 0.518757 | 5 |

### F4

| Variant | Best | Average | STD | Rank |
|---|---:|---:|---:|---:|
| SCHO | 0 | 0 | 0 | 1 |
| SCHO_NT | 0 | 0 | 0 | 1 |
| SCHO_NSTF | 0 | 0 | 0 | 1 |
| SCHO_NFTF | 0.000235845 | 0.00704832 | 0.0151811 | 6 |
| SCHO_NSF | 0 | 0 | 0 | 1 |
| SCHO_NFF | 6.28023e-07 | 0.00185236 | 0.00323712 | 5 |

### F5

| Variant | Best | Average | STD | Rank |
|---|---:|---:|---:|---:|
| SCHO | 26.0561 | 28.284 | 0.717074 | 4 |
| SCHO_NT | 26.0561 | 28.2546 | 0.703264 | 3 |
| SCHO_NSTF | 27.1768 | 28.7717 | 0.428824 | 5 |
| SCHO_NFTF | 26.4716 | 28.0251 | 0.732298 | 1 |
| SCHO_NSF | 27.1768 | 28.7737 | 0.429404 | 6 |
| SCHO_NFF | 26.4716 | 28.0251 | 0.732298 | 1 |

### F6

| Variant | Best | Average | STD | Rank |
|---|---:|---:|---:|---:|
| SCHO | 9.25409e-06 | 0.30581 | 0.712377 | 1 |
| SCHO_NT | 1.02796 | 2.28504 | 0.646598 | 4 |
| SCHO_NSTF | 2.03511 | 3.55492 | 0.746359 | 6 |
| SCHO_NFTF | 1.13902 | 2.49402 | 0.660786 | 5 |
| SCHO_NSF | 0.000295161 | 1.26429 | 1.78065 | 2 |
| SCHO_NFF | 2.56814e-07 | 1.35269 | 1.35308 | 3 |

### F7

| Variant | Best | Average | STD | Rank |
|---|---:|---:|---:|---:|
| SCHO | 4.95911e-06 | 0.000115415 | 0.000113875 | 3 |
| SCHO_NT | 4.95911e-06 | 0.000115415 | 0.000113875 | 4 |
| SCHO_NSTF | 4.95911e-06 | 0.000114855 | 0.000114018 | 1 |
| SCHO_NFTF | 0.00142047 | 0.00776996 | 0.00552859 | 6 |
| SCHO_NSF | 4.95911e-06 | 0.000114855 | 0.000114018 | 1 |
| SCHO_NFF | 9.46352e-06 | 0.00235059 | 0.0042347 | 5 |

### F8

| Variant | Best | Average | STD | Rank |
|---|---:|---:|---:|---:|
| SCHO | -12569 | -7330.69 | 2735.46 | 1 |
| SCHO_NT | -7068.72 | -5468.79 | 642.055 | 5 |
| SCHO_NSTF | -7066.77 | -5660.91 | 606.836 | 4 |
| SCHO_NFTF | -5490.49 | -4012.54 | 509.825 | 6 |
| SCHO_NSF | -12563.6 | -7261.98 | 2002.17 | 2 |
| SCHO_NFF | -12569.4 | -5974.11 | 3113.47 | 3 |

### F9

| Variant | Best | Average | STD | Rank |
|---|---:|---:|---:|---:|
| SCHO | 0 | 0 | 0 | 1 |
| SCHO_NT | 0 | 0 | 0 | 1 |
| SCHO_NSTF | 0 | 0 | 0 | 1 |
| SCHO_NFTF | 1.36779e-13 | 1.92365 | 3.81098 | 6 |
| SCHO_NSF | 0 | 0 | 0 | 1 |
| SCHO_NFF | 0 | 0.260125 | 0.834218 | 5 |

### F10

| Variant | Best | Average | STD | Rank |
|---|---:|---:|---:|---:|
| SCHO | 4.44089e-16 | 4.44089e-16 | 0 | 1 |
| SCHO_NT | 4.44089e-16 | 4.44089e-16 | 0 | 1 |
| SCHO_NSTF | 4.44089e-16 | 4.44089e-16 | 0 | 1 |
| SCHO_NFTF | 5.0599e-08 | 4.02639e-07 | 2.69354e-07 | 6 |
| SCHO_NSF | 4.44089e-16 | 4.44089e-16 | 0 | 1 |
| SCHO_NFF | 1.70339e-09 | 2.03681e-07 | 1.61846e-07 | 5 |

### F11

| Variant | Best | Average | STD | Rank |
|---|---:|---:|---:|---:|
| SCHO | 0 | 0 | 0 | 1 |
| SCHO_NT | 0 | 0 | 0 | 1 |
| SCHO_NSTF | 0 | 0 | 0 | 1 |
| SCHO_NFTF | 3.68594e-14 | 0.0190596 | 0.0347948 | 6 |
| SCHO_NSF | 0 | 0 | 0 | 1 |
| SCHO_NFF | 0 | 0.01377 | 0.0355497 | 5 |

### F12

| Variant | Best | Average | STD | Rank |
|---|---:|---:|---:|---:|
| SCHO | 2.45086e-09 | 0.277974 | 0.457505 | 3 |
| SCHO_NT | 0.0675134 | 0.396071 | 0.396292 | 4 |
| SCHO_NSTF | 0.250492 | 1.13591 | 0.367838 | 6 |
| SCHO_NFTF | 0.0912329 | 0.250128 | 0.132837 | 2 |
| SCHO_NSF | 1.4247e-06 | 0.653186 | 0.672839 | 5 |
| SCHO_NFF | 6.16742e-10 | 0.0445079 | 0.169445 | 1 |

### F13

| Variant | Best | Average | STD | Rank |
|---|---:|---:|---:|---:|
| SCHO | 1.42747e-07 | 1.34984 | 1.00099 | 2 |
| SCHO_NT | 1.59087 | 2.03152 | 0.32302 | 4 |
| SCHO_NSTF | 1.56076 | 2.50927 | 0.426563 | 6 |
| SCHO_NFTF | 1.25586 | 1.7705 | 0.254119 | 3 |
| SCHO_NSF | 2.94029e-05 | 2.03851 | 1.07257 | 5 |
| SCHO_NFF | 2.04984e-07 | 1.13166 | 0.851123 | 1 |

### F14

| Variant | Best | Average | STD | Rank |
|---|---:|---:|---:|---:|
| SCHO | 0.998004 | 3.53865 | 4.24678 | 2 |
| SCHO_NT | 0.998004 | 6.1427 | 4.86188 | 5 |
| SCHO_NSTF | 0.998004 | 7.1822 | 4.79623 | 6 |
| SCHO_NFTF | 0.998004 | 5.10516 | 4.58467 | 4 |
| SCHO_NSF | 0.998004 | 4.90366 | 4.87536 | 3 |
| SCHO_NFF | 0.998004 | 2.82662 | 3.46307 | 1 |

### F15

| Variant | Best | Average | STD | Rank |
|---|---:|---:|---:|---:|
| SCHO | 0.000307765 | 0.000327087 | 1.80542e-05 | 1 |
| SCHO_NT | 0.000307765 | 0.000765352 | 0.000511329 | 4 |
| SCHO_NSTF | 0.00030789 | 0.00889365 | 0.0101844 | 5 |
| SCHO_NFTF | 0.000310109 | 0.000554579 | 0.000147811 | 3 |
| SCHO_NSF | 0.00030789 | 0.0107791 | 0.0176551 | 6 |
| SCHO_NFF | 0.000310109 | 0.000420317 | 9.42764e-05 | 2 |

### F16

| Variant | Best | Average | STD | Rank |
|---|---:|---:|---:|---:|
| SCHO | -1.03163 | -1.03163 | 2.4104e-08 | 1 |
| SCHO_NT | -1.03163 | -1.03163 | 2.4104e-08 | 1 |
| SCHO_NSTF | -1.03163 | -1.03163 | 3.39952e-08 | 3 |
| SCHO_NFTF | -1.03163 | -1.03163 | 2.79008e-06 | 5 |
| SCHO_NSF | -1.03163 | -1.03163 | 3.39952e-08 | 3 |
| SCHO_NFF | -1.03163 | -1.03163 | 2.79008e-06 | 5 |

### F17

| Variant | Best | Average | STD | Rank |
|---|---:|---:|---:|---:|
| SCHO | 0.397887 | 0.39789 | 2.97928e-06 | 3 |
| SCHO_NT | 0.397887 | 0.39789 | 2.95969e-06 | 4 |
| SCHO_NSTF | 0.397887 | 0.397889 | 2.40827e-06 | 1 |
| SCHO_NFTF | 0.397892 | 0.39811 | 0.000285014 | 5 |
| SCHO_NSF | 0.397887 | 0.397889 | 2.40827e-06 | 1 |
| SCHO_NFF | 0.397892 | 0.39811 | 0.000285014 | 5 |

### F18

| Variant | Best | Average | STD | Rank |
|---|---:|---:|---:|---:|
| SCHO | 3 | 7.58197 | 15.585 | 3 |
| SCHO_NT | 3 | 7.58197 | 15.585 | 3 |
| SCHO_NSTF | 3 | 8.89711 | 17.3724 | 5 |
| SCHO_NFTF | 3 | 3.00001 | 1.57633e-05 | 1 |
| SCHO_NSF | 3 | 8.89711 | 17.3724 | 5 |
| SCHO_NFF | 3 | 3.00001 | 1.57633e-05 | 1 |

### F19

| Variant | Best | Average | STD | Rank |
|---|---:|---:|---:|---:|
| SCHO | -3.86278 | -3.86189 | 0.00236845 | 3 |
| SCHO_NT | -3.86278 | -3.86189 | 0.00236845 | 3 |
| SCHO_NSTF | -3.86278 | -3.86252 | 0.00139782 | 1 |
| SCHO_NFTF | -3.86276 | -3.85949 | 0.00351112 | 5 |
| SCHO_NSF | -3.86278 | -3.86252 | 0.00139782 | 1 |
| SCHO_NFF | -3.86276 | -3.85949 | 0.00351112 | 5 |

### F20

| Variant | Best | Average | STD | Rank |
|---|---:|---:|---:|---:|
| SCHO | -3.32213 | -3.26812 | 0.077065 | 3 |
| SCHO_NT | -3.32213 | -3.26812 | 0.077065 | 3 |
| SCHO_NSTF | -3.32225 | -3.27815 | 0.0669393 | 1 |
| SCHO_NFTF | -3.32047 | -3.17686 | 0.124442 | 5 |
| SCHO_NSF | -3.32225 | -3.27815 | 0.0669393 | 1 |
| SCHO_NFF | -3.32047 | -3.17686 | 0.124442 | 5 |

### F21

| Variant | Best | Average | STD | Rank |
|---|---:|---:|---:|---:|
| SCHO | -10.1532 | -8.79606 | 2.27981 | 1 |
| SCHO_NT | -10.1405 | -5.7961 | 3.25406 | 6 |
| SCHO_NSTF | -10.1471 | -6.03508 | 3.31023 | 5 |
| SCHO_NFTF | -9.98427 | -6.51553 | 2.83997 | 4 |
| SCHO_NSF | -10.1532 | -8.79171 | 2.27656 | 2 |
| SCHO_NFF | -10.1532 | -7.87493 | 2.67855 | 3 |

### F22

| Variant | Best | Average | STD | Rank |
|---|---:|---:|---:|---:|
| SCHO | -10.4028 | -9.33643 | 2.1534 | 2 |
| SCHO_NT | -10.3957 | -5.88602 | 3.32831 | 5 |
| SCHO_NSTF | -10.4 | -5.88465 | 3.33628 | 6 |
| SCHO_NFTF | -10.2408 | -7.04049 | 2.71259 | 4 |
| SCHO_NSF | -10.4028 | -9.33712 | 2.15296 | 1 |
| SCHO_NFF | -10.4028 | -8.33247 | 3.02315 | 3 |

### F23

| Variant | Best | Average | STD | Rank |
|---|---:|---:|---:|---:|
| SCHO | -10.5363 | -9.12536 | 2.64147 | 2 |
| SCHO_NT | -10.5295 | -5.13308 | 3.37601 | 6 |
| SCHO_NSTF | -10.5333 | -5.63573 | 3.5835 | 5 |
| SCHO_NFTF | -10.3733 | -6.61228 | 3.05414 | 4 |
| SCHO_NSF | -10.5363 | -9.66012 | 2.29346 | 1 |
| SCHO_NFF | -10.5363 | -7.58412 | 3.47871 | 3 |

## Interpretation boundary

`H4e RESULT: PASS` means all 4140 protocol runs completed and the
Table-5-style statistics/ranks were produced.

It does **not** mean the five controlled structural variants numerically
match the unrecovered author variant implementations.

H4f must compare the reproduced Table-5 statistics/ranking against the
paper and freeze any disagreement without parameter tuning.