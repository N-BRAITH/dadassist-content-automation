# Pexels Video Library - Categories & Metadata

**Date:** December 7, 2025  
**Total Videos:** 21 source videos  
**Prestitched Videos:** 2

---

## 📦 Current Prestitched Videos

### **Prestitched Background #6**
**Tags:** parenting, children, family, legal, custody, support, rights, care, bonding, professional, advice, wellness, communication

**Theme:** General family law and parenting support

---

### **Prestitched Background #7** ⭐ (Currently Used)
**Tags:** parenting, legal, custody, rights, family, children, support, wellness, communication, professional, advice, court, separation, divorce, mediation, agreement

**Theme:** Legal proceedings and family separation (court, divorce, mediation)

✅ **You are CORRECT** - #7 is focused on parenting but with emphasis on legal/court aspects

---

## 🎬 Source Pexels Videos (21 videos)

All videos downloaded to: `/Users/nicholasbraithwaite/Documents/pexels-videos/`

| Video File | Size | Likely Theme |
|------------|------|--------------|
| pexels_3120663.mp4 | 43 MB | Family/Father-child |
| pexels_3135808.mp4 | 4.1 MB | Professional/Meeting |
| pexels_3188951.mp4 | 2.2 MB | Legal/Documents |
| pexels_3252974.mp4 | 26 MB | Business/Corporate |
| pexels_3326745.mp4 | 5.9 MB | Communication/Phone |
| pexels_34421873.mp4 | 8.0 MB | Modern/Professional |
| pexels_3738655.mp4 | 8.7 MB | Documents/Paperwork |
| pexels_4512203.mp4 | 7.7 MB | Legal/Court |
| pexels_4812264.mp4 | 45 MB | Court/Justice |
| pexels_4988395.mp4 | 11 MB | Support/Help |
| pexels_5320011.mp4 | 10 MB | Planning/Strategy |
| pexels_5544312.mp4 | 8.9 MB | Family/Support |
| pexels_5713278.mp4 | 22 MB | Planning/Thinking |
| pexels_6101325.mp4 | 24 MB | Family/Father-child |
| pexels_6565218.mp4 | 37 MB | Resolution/Success |
| pexels_7039914.mp4 | 20 MB | Consultation/Meeting |
| pexels_7735488.mp4 | 6.8 MB | Handshake/Agreement |
| pexels_8061655.mp4 | 23 MB | Business/Meeting |
| pexels_8135731.mp4 | 15 MB | Consultation/Advice |
| pexels_8747244.mp4 | 32 MB | Business/Professional |
| pexels_8747881.mp4 | 26 MB | Stress/Difficulty |

**Total Size:** ~386 MB

---

## 🎯 Suggested New Prestitched Video Categories

Based on the available source videos and DadAssist content themes, here are recommended categories:

### **Category 1: Emotional Support & Wellness**
**Focus:** Mental health, stress management, emotional wellbeing  
**Suggested Videos:**
- pexels_8747881.mp4 (stress/difficulty)
- pexels_4988395.mp4 (support/help)
- pexels_6565218.mp4 (resolution/success)
- pexels_5544312.mp4 (family/support)
- pexels_6101325.mp4 (family bonding)

**Tags:** wellness, mental-health, stress, support, emotional, wellbeing, coping, resilience

---

### **Category 2: Legal Proceedings & Court**
**Focus:** Court processes, legal representation, formal proceedings  
**Suggested Videos:**
- pexels_4812264.mp4 (court/justice)
- pexels_4512203.mp4 (legal/court)
- pexels_3188951.mp4 (legal documents)
- pexels_3738655.mp4 (documents/paperwork)
- pexels_8061655.mp4 (business/professional)

**Tags:** court, legal, proceedings, justice, formal, representation, lawyer, judge, hearing

---

### **Category 3: Mediation & Agreement**
**Focus:** Negotiation, mediation, reaching agreements  
**Suggested Videos:**
- pexels_7735488.mp4 (handshake/agreement)
- pexels_7039914.mp4 (consultation/meeting)
- pexels_8135731.mp4 (consultation/advice)
- pexels_3135808.mp4 (professional meeting)
- pexels_5320011.mp4 (planning/strategy)

**Tags:** mediation, negotiation, agreement, compromise, settlement, discussion, resolution

---

### **Category 4: Father-Child Bonding**
**Focus:** Positive parenting, father-child relationships, quality time  
**Suggested Videos:**
- pexels_3120663.mp4 (father-child)
- pexels_6101325.mp4 (family bonding)
- pexels_5544312.mp4 (family support)
- pexels_6565218.mp4 (positive outcomes)

**Tags:** parenting, bonding, children, father, relationship, care, love, quality-time, activities

---

### **Category 5: Professional Advice & Planning**
**Focus:** Getting professional help, planning ahead, strategy  
**Suggested Videos:**
- pexels_5713278.mp4 (planning/thinking)
- pexels_5320011.mp4 (planning/strategy)
- pexels_3252974.mp4 (business/corporate)
- pexels_8747244.mp4 (business/professional)
- pexels_3326745.mp4 (communication)

**Tags:** professional, advice, planning, strategy, preparation, guidance, expert, consultation

---

### **Category 6: Communication & Co-Parenting**
**Focus:** Communication with ex-partner, co-parenting strategies  
**Suggested Videos:**
- pexels_3326745.mp4 (communication/phone)
- pexels_7039914.mp4 (consultation/meeting)
- pexels_3135808.mp4 (professional discussion)
- pexels_7735488.mp4 (agreement)

**Tags:** communication, co-parenting, cooperation, discussion, dialogue, respect, boundaries

---

## 📋 How to Create New Prestitched Videos

### Recommended Approach:

1. **Select 8-12 videos** from the category theme
2. **Trim each to 10-15 seconds** of the best footage
3. **Arrange in emotional flow:**
   - Start: Supportive/positive (2-3 clips)
   - Middle: Challenge/process (4-6 clips)
   - End: Resolution/positive (2-3 clips)
4. **Add crossfade transitions** (0.5-1 second)
5. **Target total length:** 2.5-3 minutes (allows trimming to any 2-minute segment)
6. **Export settings:**
   - Resolution: 1920x1080
   - Frame rate: 30fps
   - Codec: H.264
   - Bitrate: ~10 Mbps

### FFmpeg Command Example:
```bash
ffmpeg -i video1.mp4 -i video2.mp4 -i video3.mp4 \
  -filter_complex "[0:v]trim=0:12,setpts=PTS-STARTPTS[v0]; \
                   [1:v]trim=0:15,setpts=PTS-STARTPTS[v1]; \
                   [2:v]trim=0:10,setpts=PTS-STARTPTS[v2]; \
                   [v0][v1]xfade=transition=fade:duration=1:offset=11[vf1]; \
                   [vf1][v2]xfade=transition=fade:duration=1:offset=25[out]" \
  -map "[out]" -c:v libx264 -r 30 -pix_fmt yuv420p prestitched_new.mp4
```

---

## 🎯 Recommended Priority Order

1. **Emotional Support & Wellness** - High demand topic
2. **Father-Child Bonding** - Core DadAssist message
3. **Mediation & Agreement** - Alternative to court
4. **Communication & Co-Parenting** - Practical daily advice
5. **Professional Advice & Planning** - Proactive approach
6. **Legal Proceedings & Court** - Already covered by #7

---

## 📊 Current vs Needed

**Current Coverage:**
- ✅ Legal/Court proceedings (prestitched #7)
- ✅ General parenting/family (prestitched #6)

**Gaps to Fill:**
- ❌ Emotional support/wellness
- ❌ Father-child bonding focus
- ❌ Mediation/agreement
- ❌ Communication/co-parenting
- ❌ Professional planning

**Recommendation:** Create 4-5 new prestitched videos to cover these themes.

---

## 🔧 Upload New Prestitched Videos

Once created, upload to S3:

```bash
aws s3 cp prestitched_background_8.mp4 \
  s3://dadassist-video-library/backgrounds/prestitched_background_8.mp4
```

Then update `video_tags.json`:
```json
{
  "backgrounds/prestitched_background_8.mp4": [
    "wellness", "mental-health", "stress", "support", "emotional"
  ]
}
```

---

## 📝 Notes

- All source videos are now in `/Users/nicholasbraithwaite/Documents/pexels-videos/`
- Review each video to confirm themes match descriptions
- Consider creating 10-15 second "best moment" clips from each
- Maintain consistent visual quality across prestitched videos
- Test each new prestitched video with the pipeline before deploying
