# Number Patterns: speak digit runs in user-defined groups.
# Copyright (C) 2026 Mehran Latifi
# This file is covered by the GNU General Public License version 2.
# See the file COPYING for more details.

"""Reads runs of digits in groups, e.g. a phone number 09123456789 as 0912 34 56 789.

Patterns are written as group sizes separated by dashes, e.g. ``4-2-2-3``.
A pattern is applied to a run of digits whose length equals the sum of its groups.
Optionally, any other run of digits can be split into fixed-size groups.
"""

import re

import addonHandler
import config
import globalPluginHandler
import gui
import ui
import wx
from gui import guiHelper, nvdaControls
from gui.settingsDialogs import NVDASettingsDialog, SettingsPanel
from scriptHandler import script
from speech.extensions import filter_speechSequence

addonHandler.initTranslation()

CONFIG_SECTION = "numberPatterns"
config.conf.spec[CONFIG_SECTION] = {
	"enabled": "boolean(default=True)",
	"patterns": 'string_list(default=list("4-3-4"))',
	"fixedGroupSize": "integer(default=0, min=0, max=10)",
	"minimumLength": "integer(default=5, min=2, max=50)",
	"pauseBetweenGroups": "boolean(default=False)",
}

_PATTERN_RE = re.compile(r"^\s*\d+(\s*-\s*\d+)*\s*$")
# A run of digits not touching other digits, and not part of a decimal number like 3.14159.
_DIGIT_RUN_RE = re.compile(r"(?<![\d.,٫٬])[0-9۰-۹٠-٩]+(?![\d]|[.,٫٬]\d)")


def parsePattern(text: str) -> tuple[int, ...] | None:
	"""Turn "4-2-2-3" into (4, 2, 2, 3). Returns None if the text is not a valid pattern."""
	if not _PATTERN_RE.match(text):
		return None
	groups = tuple(int(g) for g in text.split("-"))
	if any(g <= 0 for g in groups) or len(groups) < 2:
		return None
	return groups


def _conf():
	return config.conf[CONFIG_SECTION]


def _patternsByLength() -> dict[int, tuple[int, ...]]:
	result: dict[int, tuple[int, ...]] = {}
	for text in _conf()["patterns"]:
		groups = parsePattern(text)
		if groups:
			# The first pattern defined for a given length wins.
			result.setdefault(sum(groups), groups)
	return result


def _split(digits: str, groups: tuple[int, ...]) -> list[str]:
	parts = []
	pos = 0
	for size in groups:
		parts.append(digits[pos : pos + size])
		pos += size
	return parts


def groupDigits(text: str) -> str:
	conf = _conf()
	patterns = _patternsByLength()
	fixedSize = conf["fixedGroupSize"]
	minLength = conf["minimumLength"]
	separator = ", " if conf["pauseBetweenGroups"] else " "

	def replace(match: re.Match) -> str:
		digits = match.group(0)
		groups = patterns.get(len(digits))
		if groups:
			parts = _split(digits, groups)
		elif fixedSize and len(digits) >= minLength and len(digits) > fixedSize:
			parts = [digits[i : i + fixedSize] for i in range(0, len(digits), fixedSize)]
		else:
			return digits
		return separator.join(parts)

	return _DIGIT_RUN_RE.sub(replace, text)


def _filterSpeechSequence(speechSequence):
	if not _conf()["enabled"]:
		return speechSequence
	return [groupDigits(item) if isinstance(item, str) else item for item in speechSequence]


class NumberPatternsPanel(SettingsPanel):
	# Translators: Title of the Number Patterns settings panel.
	title = _("Number Patterns")

	def makeSettings(self, settingsSizer):
		sHelper = guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
		conf = _conf()

		self.enabledCheckBox = sHelper.addItem(
			# Translators: Checkbox in the Number Patterns settings panel.
			wx.CheckBox(self, label=_("&Read numbers using patterns")),
		)
		self.enabledCheckBox.SetValue(conf["enabled"])

		self.patternsEdit = sHelper.addLabeledControl(
			# Translators: Label of the multi-line edit box holding the patterns, one per line.
			_("&Patterns, one per line (group sizes separated by dashes, e.g. 4-2-2-3):"),
			wx.TextCtrl,
			style=wx.TE_MULTILINE,
			size=(-1, 120),
		)
		self.patternsEdit.SetValue("\n".join(conf["patterns"]))

		self.fixedGroupEdit = sHelper.addLabeledControl(
			# Translators: Label of a spin control in the Number Patterns settings panel.
			_("For other numbers, read in &groups of (0 = off):"),
			nvdaControls.SelectOnFocusSpinCtrl,
			min=0,
			max=10,
			initial=conf["fixedGroupSize"],
		)

		self.minLengthEdit = sHelper.addLabeledControl(
			# Translators: Label of a spin control in the Number Patterns settings panel.
			_("Only group numbers with at least this many &digits:"),
			nvdaControls.SelectOnFocusSpinCtrl,
			min=2,
			max=50,
			initial=conf["minimumLength"],
		)

		self.pauseCheckBox = sHelper.addItem(
			# Translators: Checkbox in the Number Patterns settings panel.
			wx.CheckBox(self, label=_("P&ause between groups")),
		)
		self.pauseCheckBox.SetValue(conf["pauseBetweenGroups"])

	def _patternLines(self) -> list[str]:
		return [line.strip() for line in self.patternsEdit.GetValue().splitlines() if line.strip()]

	def isValid(self) -> bool:
		bad = [line for line in self._patternLines() if parsePattern(line) is None]
		if bad:
			gui.messageBox(
				# Translators: Error shown when a pattern is not valid. {pattern} is the invalid line.
				_("This pattern is not valid: {pattern}\nWrite group sizes separated by dashes, for example 4-2-2-3.").format(
					pattern=bad[0],
				),
				# Translators: Title of the invalid pattern error.
				_("Invalid pattern"),
				wx.OK | wx.ICON_ERROR,
				self,
			)
			self.patternsEdit.SetFocus()
			return False
		return super().isValid()

	def onSave(self):
		conf = _conf()
		conf["enabled"] = self.enabledCheckBox.IsChecked()
		conf["patterns"] = [line.replace(" ", "") for line in self._patternLines()]
		conf["fixedGroupSize"] = self.fixedGroupEdit.GetValue()
		conf["minimumLength"] = self.minLengthEdit.GetValue()
		conf["pauseBetweenGroups"] = self.pauseCheckBox.IsChecked()


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	# Translators: Input gestures category for this add-on.
	scriptCategory = _("Number Patterns")

	def __init__(self):
		super().__init__()
		NVDASettingsDialog.categoryClasses.append(NumberPatternsPanel)
		filter_speechSequence.register(_filterSpeechSequence)

	def terminate(self):
		filter_speechSequence.unregister(_filterSpeechSequence)
		try:
			NVDASettingsDialog.categoryClasses.remove(NumberPatternsPanel)
		except ValueError:
			pass
		super().terminate()

	@script(
		# Translators: Description of the command that turns number patterns on or off.
		description=_("Turns reading numbers using patterns on or off"),
	)
	def script_toggleNumberPatterns(self, gesture):
		conf = _conf()
		conf["enabled"] = not conf["enabled"]
		# Translators: Reported when number patterns are turned on or off.
		ui.message(_("Number patterns on") if conf["enabled"] else _("Number patterns off"))
