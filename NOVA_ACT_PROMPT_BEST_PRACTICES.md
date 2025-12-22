# Nova Act Prompt Best Practices Guide

## 📚 Table of Contents
1. [Core Principles](#core-principles)
2. [The Golden Rules](#the-golden-rules)
3. [Instruction Patterns](#instruction-patterns)
4. [Hybrid Approach](#hybrid-approach)
5. [Common Mistakes](#common-mistakes)
6. [Real Examples from Our Codebase](#real-examples-from-our-codebase)
7. [Timing & Waits](#timing--waits)
8. [Troubleshooting](#troubleshooting)

---

## 🎯 Core Principles

Nova Act is an **LLM-powered automation tool** that:
- Uses AI to "see" and "understand" the UI
- Makes decisions about which elements to click
- Has **non-deterministic behavior** (different results each run)
- Works best with **clear, specific, simple instructions**

### Why Nova Act is Inconsistent

1. **Non-deterministic AI Model**
   - LLM inference has randomness
   - Each run may "interpret" UI slightly differently
   - Same instruction ≠ same action every time

2. **UI State Variations**
   - Elements may render at different positions
   - Animations/transitions not fully complete
   - Browser window size affects layout

3. **Vague Instructions**
   - "that button", "this field" → AI guesses
   - Multiple valid interpretations → random choice
   - Complex multi-step instructions → confusion

---

## ⚡ The Golden Rules

### Rule 1: ONE Action Per Instruction
```python
# ❌ BAD: Multiple actions in one instruction
"Click the x button to clear the field, then click the dropdown to open it"

# ✅ GOOD: Split into separate actions
"Click the x button to clear the Role field"
time.sleep(0.5)
"Click the Role dropdown arrow to open the selector"
```

### Rule 2: Be Specific About Location/Context
```python
# ❌ BAD: Vague reference
"Click the button"
"Click the x button"

# ✅ GOOD: Provide context
"Click the Search button in the filters section"
"In the Role field, click the x button to clear the value"
```

### Rule 3: Never Use "that", "this", "it"
```python
# ❌ BAD: Vague pronouns
"Type the username into that field"
"Click on it to open the menu"

# ✅ GOOD: Use explicit names
"Type the username into the Login field"
"Click the Actions dropdown to open the menu"
```

### Rule 4: Include Visual Cues When Possible
```python
# ❌ BAD: No visual cues
"Click the submit button"

# ✅ GOOD: Add color, icon, or position
"Click the blue Save button at the bottom"
"Click the search icon button (magnifying glass)"
"Click the dropdown arrow on the right side of the Role field"
```

### Rule 5: Use Present Tense, Active Voice
```python
# ❌ BAD: Passive or unclear
"The search button should be clicked"
"Try to click the button"

# ✅ GOOD: Direct, active commands
"Click the Search button"
"Type the username into the Login field"
```

---

## 🎨 Instruction Patterns

### Pattern 1: Click Button/Link
```python
# Template
"Click the [BUTTON_NAME] button"
"Click the [LINK_TEXT] link"

# Examples
self.nova.act("Click the Search button")
self.nova.act("Click the Save button at the bottom right")
self.nova.act("Click the More filters link")
```

### Pattern 2: Click Input Field
```python
# Template
"Click the [FIELD_NAME] field"
"Click the [FIELD_NAME] input field"

# Examples
self.nova.act("Click the Login field")
self.nova.act("Click the Email input field")
self.nova.act("Click the search input field inside the Role dropdown")
```

### Pattern 3: Click Dropdown
```python
# Template
"Click the [FIELD_NAME] dropdown [arrow/button] to open the [selector/menu]"

# Examples
self.nova.act("Click the Role dropdown arrow to open the role selector")
self.nova.act("Click the Actions dropdown to open the menu")
self.nova.act("Click the Country dropdown button to open the list")
```

### Pattern 4: Select from List/Dropdown
```python
# Template
"In the [LOCATION], click on the [ITEM] option"
"In the [LIST_NAME] list, click on [ITEM_NAME]"

# Examples
self.nova.act("In the role list, click on the CSP_Inquiry option")
self.nova.act("In the Actions dropdown menu, select Edit")
self.nova.act("In the filtered results, click on the first user row")
```

### Pattern 5: Clear Field
```python
# Template
"In the [FIELD_NAME] field, click the x button to clear the [current value/value]"

# Examples
self.nova.act("In the Role field, click the x button to clear the current role value")
self.nova.act("Click the x button to clear the search field")
```

### Pattern 6: Navigate Tabs
```python
# Template
"Click the [TAB_NAME] tab"

# Examples
self.nova.act("Click the Roles tab in the Edit user modal")
self.nova.act("Click the Settings tab")
```

### Pattern 7: Complex Selection with Context
```python
# Template
"In the [TABLE/LIST], [ACTION] the [ROW/ITEM] and [SECONDARY_ACTION]"

# Examples
self.nova.act("In the results table, click the first row's Actions dropdown and select Edit")
self.nova.act("In the user list, find the row with username 'john.doe' and click the edit icon")
```

---

## 🔀 Hybrid Approach: Nova Act + Playwright

**The BEST approach for reliability**: Use Nova Act for clicking, Playwright for typing.

### Why Hybrid?

| Aspect | Nova Act Typing | Playwright Typing |
|--------|-----------------|-------------------|
| Reliability | ❌ 50-70% | ✅ 99.9% |
| Speed | 🐌 Slow (AI thinking) | ⚡ Fast |
| Context Loss | ❌ Forgets focus | ✅ Types immediately |
| Debugging | 😵 Hard | ✅ Easy |

### Hybrid Pattern

```python
class MyHandler:
    def __init__(self, nova: NovaAct):
        self.nova = nova
        self.page = nova.page  # ← Access Playwright

    def search_user(self, username: str):
        # Step 1: Nova Act clicks to focus
        self.nova.act("Click the Login field")
        time.sleep(0.3)

        # Step 2: Playwright types reliably
        self.page.keyboard.press("Control+A")  # Clear
        self.page.keyboard.type(username)      # Type
        time.sleep(0.3)

        # Step 3: Nova Act clicks button
        self.nova.act("Click the Search button")
```

### Real Example from Our Codebase

```python
# From: csp_user_search_handler.py (✅ GOOD)

def search_and_open_edit(self, target_user: str):
    # Nova Act: Click field
    self.action_counter.safe_act(self.nova, "Click the Login field")
    time.sleep(0.3)

    # Playwright: Type username (secure, no logs)
    self.page.keyboard.press("Control+A")
    self.page.keyboard.type(target_user)
    time.sleep(0.3)

    # Nova Act: Click button
    self.action_counter.safe_act(self.nova, "Click the Search button")
```

### When to Use Hybrid

✅ **Use Playwright for:**
- Typing text (usernames, passwords, search queries)
- Keyboard shortcuts (Ctrl+A, Ctrl+C, Enter)
- Sensitive data (no AI logs)
- Critical reliability needs

✅ **Use Nova Act for:**
- Clicking buttons, links, dropdowns
- Visual selection from lists
- Dynamic UI elements without fixed selectors
- UI exploration

---

## ❌ Common Mistakes

### Mistake 1: Combining Multiple Actions
```python
# ❌ BAD
"Click the x button next to the role to clear it, then click the dropdown to open it"

# ✅ GOOD
"In the Role field, click the x button to clear the current role value"
time.sleep(0.5)
"Click the Role dropdown arrow to open the role selector"
```

### Mistake 2: Using Vague Pronouns
```python
# ❌ BAD
"Click on that button"
"Type the text into that field"
"Select it from the list"

# ✅ GOOD
"Click the Save button"
"Type the username into the Login field"
"Select CSP_Inquiry from the role list"
```

### Mistake 3: No Context for Ambiguous Elements
```python
# ❌ BAD
"Click the button"  # Which button? There are 10 buttons!
"Click the x button"  # Which x? Close modal? Clear field?

# ✅ GOOD
"Click the Save button at the bottom right"
"In the Role field, click the x button to clear the value"
```

### Mistake 4: Using Nova Act for Typing
```python
# ❌ BAD - Nova Act typing is unreliable
self.nova.act(f"Type '{username}' into the Login field")

# ✅ GOOD - Playwright typing is 100% reliable
self.nova.act("Click the Login field")
time.sleep(0.3)
self.page.keyboard.type(username)
```

### Mistake 5: Insufficient Wait Times
```python
# ❌ BAD - Too fast, UI not ready
self.nova.act("Click the dropdown")
# No wait!
self.nova.act("Select option from dropdown")  # Dropdown not open yet!

# ✅ GOOD - Proper waits
self.nova.act("Click the dropdown")
time.sleep(1)  # Wait for dropdown to open
self.nova.act("Select option from dropdown")
```

### Mistake 6: Ignoring UI State
```python
# ❌ BAD - Assumes UI is ready
self.nova.act("Click the Save button")  # Button might be disabled!

# ✅ GOOD - Wait for UI to be ready
wait_for_loading_complete(self.nova, timeout_seconds=10)
self.nova.act("Click the Save button")
```

---

## 📋 Real Examples from Our Codebase

### Example 1: User Search (✅ EXCELLENT)

**File:** `csp_user_search_handler.py`

```python
def search_and_open_edit(self, target_user: str) -> bool:
    # ✅ Expand filters
    self.action_counter.safe_act(self.nova, "Click 'More filters' if visible")
    time.sleep(0.5)

    # ✅ Click field - specific, clear
    self.action_counter.safe_act(self.nova, "Click the Login field")
    time.sleep(0.3)

    # ✅ Hybrid: Playwright typing (secure, reliable)
    self.page.keyboard.press("Control+A")
    self.page.keyboard.type(target_user)
    time.sleep(0.3)

    # ✅ Click button - simple action
    self.action_counter.safe_act(self.nova, "Click the Search button")
    time.sleep(2)

    # ✅ Complex action with full context
    self.action_counter.safe_act(
        self.nova,
        "In the results table, click the first row's Actions dropdown and select Edit"
    )
    time.sleep(3)
```

**Why this works:**
- One action per instruction
- Hybrid approach (Playwright for typing)
- Proper wait times
- Clear, specific instructions
- Full context for complex actions

### Example 2: Role Change (Before Fix - ❌ BAD)

```python
# ❌ BAD: Multiple actions combined
self.nova.act(
    "Click the x button next to the current role to clear it, "
    "then click on the dropdown field to open the role selector"
)

# ❌ BAD: Nova Act typing (unreliable)
self.nova.act(
    f"Click on the empty search box inside the opened dropdown, "
    f"then type '{new_role}' to filter the roles"
)

# ❌ BAD: Vague pronoun
self.nova.act(f"Type '{new_role}' into that search box to filter the roles")
```

### Example 3: Role Change (After Fix - ✅ GOOD)

```python
# ✅ GOOD: Clear current role
self.action_counter.safe_act(
    self.nova,
    "In the Role field, click the x button to clear the current role value"
)
time.sleep(1)

# ✅ GOOD: Open dropdown
self.action_counter.safe_act(
    self.nova,
    "Click the Role dropdown arrow to open the role selector"
)
time.sleep(1)

# ✅ GOOD: Click search field
self.action_counter.safe_act(
    self.nova,
    "Click the search input field inside the Role dropdown"
)
time.sleep(0.5)

# ✅ EXCELLENT: Hybrid - Playwright typing
logger.debug(f"Typing role name: {new_role}")
self.page.keyboard.type(new_role)
time.sleep(1.5)

# ✅ GOOD: Select with context
self.action_counter.safe_act(
    self.nova,
    f"In the filtered role list, click on the role option that matches '{new_role}'"
)
time.sleep(1)
```

---

## ⏱️ Timing & Waits

### Wait Time Guidelines

| Action Type | Recommended Wait | Reason |
|-------------|------------------|--------|
| Simple click (button) | 0.3-0.5s | Let UI respond |
| Dropdown open | 0.5-1s | Animation complete |
| Modal open | 1-2s | Full render |
| Search/API call | 2-3s | Server response |
| Page navigation | 3-5s | Page load |
| Complex form load | 5-10s | Multiple elements |

### Wait Patterns

```python
# Pattern 1: Simple action
self.nova.act("Click the button")
time.sleep(0.5)

# Pattern 2: Dropdown
self.nova.act("Click the dropdown")
time.sleep(1)  # Wait for dropdown to open
self.nova.act("Select option from dropdown")

# Pattern 3: API call
self.nova.act("Click the Search button")
time.sleep(2)  # Wait for search results

# Pattern 4: Modal/Form
self.nova.act("Click the Edit button")
time.sleep(3)  # Wait for modal to fully load

# Pattern 5: Custom wait utility
wait_for_loading_complete(
    self.nova,
    timeout_seconds=10,
    action_description="Search results to load"
)
```

### Progressive Timing Strategy

If actions are failing, increase waits progressively:

```python
# Start conservative
time.sleep(1)

# If fails, increase
time.sleep(1.5)

# If still fails, increase more
time.sleep(2)

# Add custom wait logic
wait_for_loading_complete(self.nova, timeout_seconds=20)
```

---

## 🔧 Troubleshooting

### Problem 1: "Nova Act clicks wrong element"

**Cause:** Instruction too vague, multiple matching elements

**Solution:**
```python
# ❌ Before
"Click the button"

# ✅ After
"Click the blue Save button at the bottom right corner"
```

### Problem 2: "Nova Act can't find the element"

**Cause:**
- Element not rendered yet
- Wrong timing
- Element hidden by modal/overlay

**Solution:**
```python
# Add wait
time.sleep(1.5)

# Or use custom wait utility
wait_for_loading_complete(self.nova, timeout_seconds=10)

# Or check for blockers
self.nova.act("Close the notification popup if visible")
```

### Problem 3: "Typing action fails or types in wrong place"

**Cause:** Nova Act typing is unreliable

**Solution:**
```python
# ❌ Don't use Nova Act for typing
self.nova.act("Type 'username' into the field")

# ✅ Use hybrid approach
self.nova.act("Click the field")
time.sleep(0.3)
self.page.keyboard.type("username")
```

### Problem 4: "Action works sometimes, fails other times"

**Cause:** Non-deterministic AI behavior, timing issues

**Solution:**
```python
# 1. Simplify instruction
"Click the button" → "Click the blue Save button"

# 2. Add context
"Select option" → "In the role dropdown, select the CSP_Inquiry option"

# 3. Increase waits
time.sleep(0.5) → time.sleep(1)

# 4. Use retry decorator
@with_retry(max_retries=3, retry_delay=2)
def my_action(self):
    # action code
```

### Problem 5: "Nova Act closes modal or clicks wrong thing"

**Cause:** AI gets confused, loses context

**Solution:**
```python
# 1. Add more context to instruction
# ❌ "Type into the search field"
# ✅ "Type into the search field inside the Role dropdown"

# 2. Break into smaller steps
# Don't: "Click field and type text"
# Do:
self.nova.act("Click the field")
time.sleep(0.5)
self.page.keyboard.type(text)

# 3. Use visual cues
"Click the search icon (magnifying glass) in the top right"
```

### Problem 6: "Dropdown closes before selection"

**Cause:** Insufficient wait, or click lost focus

**Solution:**
```python
# Increase wait after opening dropdown
self.nova.act("Click the dropdown arrow")
time.sleep(1.5)  # Was 0.5, now 1.5

# Be specific about where to click
self.nova.act("In the opened dropdown menu, click on the first option")
```

---

## 📊 Quick Reference: Instruction Checklist

Before writing a Nova Act instruction, check:

- [ ] Is it ONE action only?
- [ ] Does it include specific context/location?
- [ ] Does it avoid "that", "this", "it"?
- [ ] Does it use active voice?
- [ ] Does it include visual cues if ambiguous?
- [ ] Is there proper wait time after?
- [ ] Should I use Playwright instead (for typing)?

---

## 🎓 Learning from Logs

When Nova Act fails, read the logs:

```
think("I need to close the popup to see the search field")
→ Nova Act got confused, thinks search field is behind popup
```

**Fix:** Add more context
```python
# ❌ "Type into the search field"
# ✅ "Type into the search field that is already focused inside the Role dropdown"
```

---

## 🚀 Advanced Tips

### Tip 1: Conditional Actions
```python
self.nova.act("Click 'More filters' if visible")
self.nova.act("Close the notification popup if it appears")
```

### Tip 2: Position-based Selection
```python
self.nova.act("Click the first row in the results table")
self.nova.act("Click the last option in the dropdown")
self.nova.act("Click the Save button at the bottom right")
```

### Tip 3: Icon-based Selection
```python
self.nova.act("Click the edit icon (pencil) in the first row")
self.nova.act("Click the delete icon (trash can) next to the user name")
self.nova.act("Click the search icon (magnifying glass)")
```

### Tip 4: Color-based Selection
```python
self.nova.act("Click the blue Save button")
self.nova.act("Click the red Delete button")
self.nova.act("Click the green Confirm button")
```

### Tip 5: Relative Position
```python
self.nova.act("Click the dropdown arrow on the right side of the Role field")
self.nova.act("Click the x button next to the username")
self.nova.act("Click the button below the search results")
```

---

## 📝 Summary

### DO ✅
- Write simple, single-action instructions
- Include specific context and location
- Use Playwright for typing
- Add proper wait times
- Use visual cues (color, icon, position)
- Break complex tasks into small steps
- Test and iterate

### DON'T ❌
- Combine multiple actions in one instruction
- Use vague pronouns ("that", "this", "it")
- Use Nova Act for typing
- Skip wait times
- Assume elements are immediately ready
- Write ambiguous instructions

---

## 📚 Additional Resources

- **Action Counter**: Prevents infinite loops (max_actions limit)
- **Retry Decorator**: `@with_retry(max_retries=3)` for flaky actions
- **Wait Utility**: `wait_for_loading_complete()` for dynamic content
- **Logging**: Always log actions for debugging

---

**Document Version:** 1.0
**Last Updated:** 2025-12-22
**Maintainer:** CSP Automation Team
