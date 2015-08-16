// Copyright (c) 2012, the Dart project authors.  Please see the AUTHORS file
// for details. All rights reserved. Use of this source code is governed by a
// BSD-style license that can be found in the LICENSE file.
import 'dart:html';
import 'dart:math' show Random;
import 'dart:convert' show JSON;
import 'dart:async' show Future;
// This app starts out with almost no Dart code, as described
// in Step 1 of the code lab (dartlang.org/codelabs/darrrt/).
ButtonElement genButton;
SpanElement badgeNameElement;

main() async {
  // Your app starts here.
  InputElement inputField = querySelector('#inputName');
  inputField.onInput.listen(updateBadge);
  genButton = querySelector('#generateButton');
  genButton.onClick.listen(generateBadge);
  badgeNameElement = querySelector('#badgeName');
    // async logic
  try {
    await PirateName.readyThePirates();
    // on success
    inputField.disabled = false;
    genButton.disabled = false;
  } catch (arrr) {
    print('Error initializing pirate names: $arrr');
    badgeNameElement.text = 'Arr! No names.';
  }
}
void updateBadge(Event e) {
  String inputName = (e.target as InputElement).value;
  setBadgeName(new PirateName(firstName: inputName));
    if (inputName.trim().isEmpty) {
        genButton..disabled = false
                     ..text = 'Aye! Gimme a name!';
  } else {
    genButton..disabled = true
             ..text = 'Arre! Write yer name!';
  }
}
void setBadgeName(PirateName newName) {
  querySelector('#badgeName').text = newName.pirateName;
}
void generateBadge(Event e) {
  setBadgeName(new PirateName());
}
class PirateName {
  static final Random indexGen = new Random();
  String _firstName;
  String _appellation;

  static List<String> names = [];
  static List<String> appellations = [];
  
  PirateName({String firstName, String appellation}) {
    if (firstName == null) {
      _firstName = names[indexGen.nextInt(names.length)];
    } else {
      _firstName = firstName;
    }
    if (appellation == null) {
      _appellation = appellations[indexGen.nextInt(appellations.length)];
    } else {
      _appellation = appellation;
    }
  }
  
  String get pirateName =>
    _firstName.isEmpty ? '': '$_firstName the $_appellation';
  String get jsonString =>
    JSON.encode({"f": _firstName, "a": _appellation});
  String toString() => pirateName;
  
  static Future readyThePirates() async {
    String path =
        'https://www.dartlang.org/codelabs/darrrt/files/piratenames.json';
    String jsonString = await HttpRequest.getString(path);
    _parsePirateNamesFromJSON(jsonString);
  }

  static _parsePirateNamesFromJSON(String jsonString) {
    Map pirateNames = JSON.decode(jsonString);
    names = pirateNames['names'];
    appellations = pirateNames['appellations'];
  }
};