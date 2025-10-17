# LBPH Model Testing Guide

This guide explains how to test your trained LBPH face recognition model using the provided test scripts.

---

## Available Test Scripts

### 1. `test_lbph_model.py` - Interactive Full Tester ⭐ RECOMMENDED

**Full-featured testing with menu-driven interface**

**Features:**
- ✅ Live webcam testing
- ✅ Single image testing
- ✅ Batch directory testing
- ✅ Visual feedback with color-coded results
- ✅ Detailed statistics and reports

**Usage:**
```bash
cd backend
python test_lbph_model.py
```

**Menu Options:**

```
1. Test with Webcam (Live)
   - Opens your webcam
   - Real-time face recognition
   - Press 'q' to quit, 's' to save screenshot
   - Shows confidence scores live

2. Test with Single Image
   - Test any image file
   - Shows detailed results
   - Visual display with bounding boxes
   - Press Enter to use a validation image

3. Test with Directory (Batch)
   - Test all images in a folder
   - Shows each result one by one
   - Press any key to continue, 'q' to quit
   - Final statistics summary

4. Exit
```

---

### 2. `quick_test.py` - Quick Single Image Test

**Fast command-line testing for single images**

**Usage:**
```bash
cd backend

# Test specific image
python quick_test.py path/to/image.jpg

# Test with validation image
python quick_test.py ../data/validation_images/WhatsApp Image 2025-10-12 at 14.26.42_499a7bfa.jpg

# Run without arguments to test first validation image
python quick_test.py
```

**Output Example:**
```
Testing: WhatsApp Image 2025-10-12 at 14.26.42_499a7bfa.jpg
============================================================

Face #1:
  Status:     AUTHORIZED
  Person:     owner_rajasekhar
  Confidence: 0.00
  Threshold:  0-65=Auth, 65-70=Uncertain, 70+=Intruder
```

---

### 3. `validate_in_memory.py` - Full Validation Report

**Comprehensive validation on all 65 validation images**

**Usage:**
```bash
cd backend
python validate_in_memory.py
```

**Output:**
- Processes all 65 validation images
- Shows recognition results for each
- Final statistics report
- 96.2% accuracy achieved ✅

---

## Understanding Results

### Recognition Status

| Status | Confidence | Color | Meaning |
|--------|-----------|-------|---------|
| ✅ **AUTHORIZED** | 0-65 | Green | Known person - Access granted |
| ⚠️ **UNCERTAIN** | 65-70 | Orange | Possible match - Manual verification |
| 🚨 **INTRUDER** | 70+ | Red | Unknown person - Alert triggered |

### Confidence Scores

- **Lower = Better match**
- **0.0 = Perfect match** (identical to training image)
- **65 = Threshold** (authorization cutoff)
- **70+ = Intruder** (definitely not authorized)

---

## Testing Workflows

### Workflow 1: Quick Test of New Person
```bash
# Take a photo
# Save as test_photo.jpg

# Test it
cd backend
python quick_test.py test_photo.jpg
```

### Workflow 2: Live Webcam Testing
```bash
cd backend
python test_lbph_model.py

# Select option 1 (Webcam)
# Show your face to camera
# Press 's' to save screenshots
# Press 'q' when done
```

### Workflow 3: Batch Test Multiple Images
```bash
cd backend
python test_lbph_model.py

# Select option 3 (Directory)
# Enter: ../data/validation_images
# Review each result
# Press any key to continue, 'q' to stop
```

### Workflow 4: Full Validation Report
```bash
cd backend
python validate_in_memory.py

# Processes all 65 validation images
# Shows detailed statistics
# No interaction required
```

---

## Test Image Requirements

### Good Test Images:
✅ Clear frontal face view
✅ Good lighting (not too bright/dark)
✅ Face size at least 30x30 pixels
✅ Face not obscured (no masks, sunglasses)
✅ Neutral or slight angle (up to 20°)

### Poor Test Images:
❌ Face at extreme angle (>45°)
❌ Very poor lighting
❌ Face too small in frame
❌ Face partially covered
❌ Multiple faces overlapping

---

## Example Test Sessions

### Example 1: Testing Authorized Person

```bash
$ python quick_test.py ../data/validation_images/owner_image.jpg

Testing: owner_image.jpg
============================================================

Face #1:
  Status:     AUTHORIZED ✅
  Person:     owner_rajasekhar
  Confidence: 0.00
  Threshold:  0-65=Auth, 65-70=Uncertain, 70+=Intruder

Result: Access granted! Person recognized perfectly.
```

### Example 2: Testing Unknown Person

```bash
$ python quick_test.py unknown_person.jpg

Testing: unknown_person.jpg
============================================================

Face #1:
  Status:     INTRUDER 🚨
  Person:     Unknown
  Confidence: 125.43
  Threshold:  0-65=Auth, 65-70=Uncertain, 70+=Intruder

Result: ALERT! Unknown person detected - email sent!
```

### Example 3: Webcam Test Output

```
WEBCAM TEST MODE
============================================================

Instructions:
  - Position your face in front of the camera
  - Press 'q' to quit
  - Press 's' to save screenshot

Starting webcam...

[Live video feed opens]
[Green box around face]
AUTHORIZED: farmer_Basava
Confidence: 0.0

[Press 's']
[INFO] Screenshot saved: test_screenshot_1.jpg

[Press 'q']
[INFO] Exiting...
[INFO] Webcam test completed
```

---

## Troubleshooting

### Issue: "No faces detected"
**Solution:**
- Improve lighting
- Move closer to camera
- Ensure face is frontal
- Check image quality

### Issue: High confidence (70+) for known person
**Solution:**
- Add more training images for that person
- Retrain model with better quality images
- Check if lighting is very different from training

### Issue: Webcam not opening
**Solution:**
- Check webcam is connected
- Close other applications using webcam
- Try different camera index:
  - Change `cv2.VideoCapture(0)` to `cv2.VideoCapture(1)`

### Issue: Model training fails
**Solution:**
- Ensure `data/known_faces/` directory exists
- Check training images are valid (.jpg/.png)
- Verify at least one face in each training image

---

## Performance Benchmarks

Based on validation with 65 test images:

| Metric | Value |
|--------|-------|
| **Accuracy** | 96.2% |
| **Authorized Recognition** | 51/53 faces |
| **False Positives** | 0% |
| **Intruder Detection** | 100% |
| **Processing Speed** | ~30-50ms per face |

---

## Next Steps

After testing your model:

1. **If accuracy is good (>90%):**
   - ✅ Deploy to production
   - ✅ Set cameras to "LBPH Only" mode
   - ✅ Monitor alert emails

2. **If accuracy is low (<90%):**
   - Add more training images (aim for 30+ per person)
   - Improve image quality (lighting, angles)
   - Retrain model with `train_simple.py`
   - Re-validate with `validate_in_memory.py`

3. **For new authorized personnel:**
   - Create folder: `data/known_faces/person_name/`
   - Add 20-30 face images
   - Run `train_simple.py` to retrain
   - Test with `test_lbph_model.py`

---

## Quick Reference Commands

```bash
# Interactive full tester (recommended)
python test_lbph_model.py

# Quick single image test
python quick_test.py image.jpg

# Full validation report
python validate_in_memory.py

# Train/retrain model
python train_simple.py

# Webcam live test
python test_lbph_model.py
# Then select option 1
```

---

**Model Status:** ✅ Trained and validated (96.2% accuracy)  
**Authorized Personnel:** farmer_Basava, manager_prajwal, owner_rajasekhar  
**Ready for Production:** Yes 🚀
