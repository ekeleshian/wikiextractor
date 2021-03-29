import ipywidgets as widgets
from IPython.display import display
from ipywidgets import Button, HBox, VBox
import json
import pandas as pd

__all__ = ['LabelMyTextWidget']


class LabelMyTextWidget:
    """
    Widget to quickly label a dataframe containing a column with text data and a colum with target labels.
    """

    def __init__(self, df_source, content_column, class_list, class_id, output_column, unclassified_value=-1,
                 randomize=False):
        """
        Create a LabelMyTextWidget object.

        :param df_source: The pandas dataframe containingn the data column and the label column (tto fill by the widget)
        :param content_column: The name of the column containing the text data to label
        :param class_list: List of the label type names (ex: Positive, Negative, Neutral)
        :param class_id: The id of each label type
        :param output_column: Name of the column to complete with labels
        :param unclassified_value: Value of the unnclassified rows for the output_column
        :param randomize: If true, the labeling order will be random.  If false, it will follow the index numbers


        :Example:
        >>> df['text'] = 'example of text content to label'
        >>> df['label'] = -1
        >>> LabelMyText(df, 'text', ['positive, 'negative'], [1,0], 'label', uncalssified_value=-1)
        """
        self.df_source = df_source
        self.content_column = content_column
        self.output_column = output_column
        self.unclassified_value = unclassified_value
        self.randomize = randomize
        self.file_index = 0
        self.count = 0

        self.items = [ButtonLabeling(class_id=class_id[i], description=l) for i, l in enumerate(class_list)]
        self.items.append(ButtonLabeling(class_id=unclassified_value, description="Skip", button_style='warning'))

        for button in self.items:
            button.on_click(self.on_button_clicked_t)

        self.out = widgets.Output(layout={'border': '1px solid black'})
        self.out.append_stderr("text is coming here")

        button_box = HBox([widgets.Label(value="Label"), *self.items])

        self.box = VBox([button_box, self.out])

        self.df_explore = self.df_source[self.df_source[output_column] == unclassified_value].index
        self.cursor = 0

        if randomize:
            self.df_explore = np.random.permutation(self.df_explore)

        self.out.clear_output(wait=True)

    def display(self):
        display(self.box)
        self.display_next_row()

    def on_button_clicked_t(self, b):
        if (self.cursor) <= len(self.df_explore) and len(self.df_explore) > 0:
            self.df_source.loc[self.df_explore[self.cursor - 1], self.output_column] = b.class_id
        if b.class_id == 1:
            self.count += 1
        self.display_next_row()

    def display_next_row(self):
        if (self.cursor) >= len(self.df_explore):
            with self.out:
                self.out.clear_output()
                print('Finished: All rows have been processed')
            return
        if self.count >= 3:
            self.count = 0
            self.file_index += 1
            self.cursor = \
            self.df_source[self.df_source['file'] == self.df_source['file'].unique()[self.file_index]].index[0]
            next_text = str(self.df_source[self.content_column].loc[self.df_explore[self.cursor]])
        else:
            next_text = str(self.df_source[self.content_column].loc[self.df_explore[self.cursor]])
        with self.out:
            rows_accepted = len(self.df_source[self.df_source['label'] == 1])
            total_files = len(self.df_source['file'].unique())
            current_file = self.df_source['file'].unique()[self.file_index]
            print(
                f'Row index {self.df_explore[self.cursor]} | Number of rows accepted: {rows_accepted} | On file {current_file} | File processing progress: {self.file_index + 1} / {total_files}\n')
            print(f'{next_text}')

        self.cursor += 1
        self.out.clear_output(wait=True)


class ButtonLabeling(Button):
    def __init__(self, class_id, *args, **kwargs):
        self.class_id = class_id
        super().__init__(*args, **kwargs)

texts = []
files = []
labels = []

ones = {'0': '00', '1': '01', '2': '02', '3': '03', '4':'04', '5': '05', "6": "06", "7": "07", "8": "08", "9": "09"}
for ch in ["A", "B", "C", "D", "E", "F", "G"]:
    for i in range(100):
        if i < 10:
            i = ones[str(i)]
        count = 0
        filename = f'text/A{ch}/wiki_{i}'
        with open(filename, 'r') as f:
            data = f.readlines()
            for idx, article in enumerate(data):
                data_json = json.loads(article)
                text = data_json['text']
                text = text.replace(":", "։")
                text_arr = text.split("։")
                text_arr = [text + '։' for text in text_arr]
                article_name = filename + f'_{idx}'
                for text in text_arr:
                    text = text.replace('\n', ' ')
                    texts.append(text)
                    files.append(filename)
                    labels.append(-1)