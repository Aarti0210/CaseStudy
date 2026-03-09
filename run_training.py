#!/usr/bin/env python
"""Quick training script to generate model artifact."""
import sys
from app.ml.train_model import train

if __name__ == "__main__":
    # NOTE: v1 model frozen for DIPEX demo – retrain only when upgrading version.
    try:
        train(n_samples=2000)
        print("\n✓ Training completed successfully")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Training failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
