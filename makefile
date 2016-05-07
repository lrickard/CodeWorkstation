all: MainWindowUI.py CommandBoxDialogUI.py ButtonDialogUI.py CommandBoxChoiceDialogUI.py ErrorDialogUI.py ShortcutSaveDialogUI.py
	@echo "Done!"

MainWindowUI.py: MainWindow.ui
	@pyuic5 $< > $@

CommandBoxDialogUI.py: CommandBoxDialog.ui
	@pyuic5 $< > $@

ShortcutSaveDialogUI.py: ShortcutSaveDialog.ui
	@pyuic5 $< > $@

ButtonDialogUI.py: ButtonDialog.ui
	@pyuic5 $< > $@

CommandBoxChoiceDialogUI.py: CommandBoxChoiceDialog.ui
	@pyuic5 $< > $@

ErrorDialogUI.py: ErrorDialog.ui
	@pyuic5 $< > $@

clean:
	@if [ -e ButtonDialogUI.py ]; then rm ButtonDialogUI.py; fi
	@if [ -e CommandBoxDialogUI.py ]; then rm CommandBoxDialogUI.py; fi
	@if [ -e MainWindowUI.py ]; then rm MainWindowUI.py; fi
	@if [ -e CommandBoxDialogUI.py ]; then rm CommandBoxDialogUI.py; fi
	@if [ -e ErrorDialogUI.py ]; then rm ErrorDialogUI.py; fi
	@if [ -e ShortcutSaveDialogUI.py ]; then rm ShortcutSaveDialogUI.py; fi
	@echo "Clean!"
