"""
Adapted from the pyLanguagetool library (a python wrapper for the LanguageTool API)
https://github.com/Findus23/pyLanguagetool/blob/master/pylanguagetool/api.py
"""
import requests
import pprint

def check(input_text, lang='en-US', mother_tongue=None, preferred_variants=None,
          enabled_rules=None, disabled_rules='EN_COMPOUNDS,TYPOS', #removing 'TYPOS' dramatically increases the mistakes
          enabled_categories=None, 
          disabled_categories='CASING,TYPOGRAPHY,EN_QUOTES,PUNCTUATION',
          enabled_only='false', ignore_list=None,
          **kwargs):
    """
    Check given text and return API response as a dictionary.

    Args:
        input_text (str):
            Plain text that will be checked for spelling mistakes.

        lang: Language of the given text as `RFC 3066`__ language code.
            For example ``en-GB`` or ``de-AT``. ``auto`` is a valid value too
            and will cause the language to be detected automatically.

            __ https://www.ietf.org/rfc/rfc3066.txt

        mother_tongue: Native language of the author as `RFC 3066`__ language
            code.

            __ https://www.ietf.org/rfc/rfc3066.txt

        preferred_variants (str):
            Comma-separated list of preferred language variants. The language
            detector used with ``language=auto`` can detect e.g. English, but
            it cannot decide whether British English or American English is
            used. Therefore, this parameter can be used to specify the
            preferred variants like ``en-GB`` and ``de-AT``. Only available
            with ``language=auto``.

        enabled_rules (str):
            Comma-separated list of IDs of rules to be enabled

        disabled_rules (str):
            Comma-separated list of IDs of rules to be disabled.

        enabled_categories (str):
            Comma-separated list of IDs of categories to be enabled.

        disabled_categories (str):
            Comma-separated list of IDs of categories to be disabled.

        enabled_only (bool):
            If ``True``, only the rules and categories whose IDs are specified
            with ``enabledRules`` or ``enabledCategories`` are enabled.
            Defaults to ``False``.

        verbose (bool):
            If ``True``, a more verbose output will be printed. Defaults to
            ``False``.

        ignore_list (List[str]):
            A custom list of words that should be excluded from spell checking errors.

    Returns:
        dict:
            A dictionary representation of the JSON API response.
            The most notable key is ``matches``, which contains a list of all
            spelling mistakes that have been found.
    """
    
    post_parameters = {
        "text": input_text,
        "language": lang,
        "motherTongue": mother_tongue,
        "preferredVariants": preferred_variants,
        "enabledRules": enabled_rules,
        "disabledRules": disabled_rules,
        "enabledCategories": enabled_categories,
        "disabledCategories": disabled_categories,
        "enabledOnly": enabled_only
    }

    post_parameters = {k: v for k, v in post_parameters.items() if v}
    resp = requests.post("https://languagetool.org/api/v2/check", data=post_parameters)

    if resp.status_code != 200:
        raise ValueError(resp.text)

    data = resp.json()
    if ignore_list:
        matches = data.pop('matches', [])
        data['matches'] = [
            match for match in matches 
            if not _is_in_ignore_list(match, ignore_list)
        ]
    # To print error matches
    # if data['matches']:
    #     pprint.pprint(data)
    return data

def _is_in_ignore_list(match, ignore_list):
    start = match['context']['offset']
    end = start + match['context']['length']
    word = match['context']['text'][start:end]
    return word in ignore_list
