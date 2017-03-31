import csv
import ast
from operator import itemgetter
from porter2stemmer import Porter2Stemmer
from Tkinter import *

def removables(list_of_dictionaries):
    set_removables = set(['aboard', 'about', 'above', 'across', 'after', 'against', 'ahead of', 'along', 'amid',
                          'amidst', 'among', 'around', 'as', 'as far as', 'as of', 'aside from', 'at', 'athwart',
                          'atop', 'barring', 'because of', 'before', 'behind', 'below', 'beneath', 'beside', 'besides',
                          'between', 'beyond', 'but', 'by',
                          'by means of', 'circa', 'concerning', 'despite', 'down', 'during', 'except', 'except for',
                          'excluding', 'far from', 'following',
                          'for', 'from', 'in', 'in accordance with', 'in addition to', 'in case of', 'in front of',
                          'in lieu of', 'in place of',
                          'in spite of', 'including', 'inside', 'instead of', 'into', 'like', 'minus', 'near',
                          'next to', 'notwithstanding', 'of', 'off',
                          'on', 'on account of', 'on behalf of', 'on top of', 'onto', 'opposite', 'out', 'out of',
                          'outside', 'over', 'past', 'plus',
                          'prior to', 'regarding', 'regardless of', 'save', 'since', 'than', 'through', 'till', 'to',
                          'toward', 'towards', 'under',
                          'underneath', 'unlike', 'until', 'up', 'upon', 'versus', 'via', 'with', 'with regard to',
                          'within', 'without',
                          ' ', 'if', 'is', 'are', 'was', 'were', 'a', 'an', 'the', 'then', 'like', 'there', 'it',
                          'that', 'here', 'and', '', 'also',
                          'no', 'not', 'while', 'who', 'what', 'when', 'where', 'whom', 'whose'])

    stemmer = Porter2Stemmer()
    for each_bug in list_of_dictionaries:
        # removing unwanted items from summary
        # applying stemming algorithm on each bug summary
        each_bug['Summary'] = [stemmer.stem(i) for i in set(each_bug['Summary']) - set_removables]
    return list_of_dictionaries


def read_new_bug(feature_from_textbox,summary_from_textbox):
    user_input_bug = {}
    bug_list = []
    user_input_bug['Feature'] = feature_from_textbox
    user_input_bug['Summary'] = summary_from_textbox.strip('\n').split(' ')
    # user_input_bug['labels']=raw_input("Enter labels: ").split(',')
    bug_list.append(user_input_bug)

    return removables(bug_list)


def construct_feature_dictionary(sample_bug_list):
    feature_dict_list = []
    feature_list = []
    sorted_bug_list = sorted(sample_bug_list, key=itemgetter('Feature'))
    [feature_list.append(each_item['Feature']) for each_item in sorted_bug_list]
    for each_feature in set(feature_list):
        feature_dict = {}
        feature_dict['Feature'] = each_feature
        new_list = []
        feature_found = False
        for each_item in sorted_bug_list:
            if each_feature == each_item['Feature']:
                new_list.append({key: value for key, value in each_item.items() if key != 'Feature'})
                feature_found = True
            if feature_found and each_feature != each_item['Feature']:
                break
        feature_dict['Details'] = new_list
        feature_dict_list.append(feature_dict)
    return feature_dict_list


def find_duplicate_bugs(user_input_bug, comparable_bug_list):
    threshould = 0.5
    flag = 0
    similar_bugs_list = []
    for each_bug in comparable_bug_list:
        if user_input_bug[0]['Feature'] == each_bug['Feature']:
            for each_detail in each_bug['Details']:
                similar_bugs_dict = {}
                # extracting similar words in summary
                len_set_diff = len(set(each_detail['Summary']) & set(user_input_bug[0]['Summary']))
                len_set = len(set(each_detail['Summary']))
                # print float(len_set_diff)/len_set
                # finding similarity ratio and comparing it with threshould
                if round((float(len_set_diff) / len_set), 2) >= threshould:
                    similar_bugs_dict['Feature'] = each_bug['Feature']
                    # similar_bugs_dict['Labels'] = each_detail['Labels']
                    similar_bugs_dict['Org_Summary'] = each_detail['Org_Summary']
                    similar_bugs_dict['Bug_ID'] = each_detail['Bug_ID']
                    similar_bugs_list.append(similar_bugs_dict)
                    flag = 1
            break
    if flag == 0:
        import tkMessageBox
        tkMessageBox.showinfo('Failure','No similar bug found!!')
        # print "No similar bug found!!"
    else:
        # print "Similar bugs found!!"
        # for eachbug in similar_bugs_list:
        #     print eachbug['Bug_ID'] + '|' + eachbug['Feature'] + '|' + eachbug['Org_Summary']
        master=Tk()
        frame = Frame(master)
        frame.pack()

        bottomframe = Frame(master)
        bottomframe.pack(side=BOTTOM)

        Label(frame, text='Similar Bugs Found!!', font=20, fg='Red', padx=20, pady=10, anchor="center").grid(row=0)
        Label(frame, text='BugID', padx=10, relief=RAISED).grid(row=1)
        Label(frame, text='Feature', padx=10, relief=RAISED).grid(row=1, column=1)
        Label(frame, text='Summary', padx=10, relief=RAISED).grid(row=1, column=2)
        count = 2
        for i in similar_bugs_list:
            Label(frame, text=i['Bug_ID'], padx=10, pady=10, relief=RAISED).grid(row=count, column=0)
            Label(frame, text=i['Feature'], padx=10, pady=10, relief=RAISED).grid(row=count, column=1)
            Label(frame, text=i['Org_Summary'], padx=10, pady=10, relief=RAISED).grid(row=count, column=2)
            count += 1
        Button(frame, text='Close', command=quit, padx=10, bd=5, font=5, pady=5, width=20).grid(row=count)
        master.mainloop()

# Reading bugs in csv file
def read_JIRA_file(filepath):
    sample_bug_list = []
    with open(filepath) as csvfilereader:
        reader = csv.reader(csvfilereader, delimiter=',', quotechar='"')
        next(reader, None)
        for row in reader:
            bugs_dict = {}
            #         Splitting the first column (summary) based on ::
            str1 = row[0].split('::')
            bugs_dict['Bug_ID'] = row[1]
            bugs_dict['Feature'] = '::'.join(str1[0:-1]).strip(
                ' ')  # taking from first item to last but one item an joining back the first part
            bugs_dict['Summary'] = str1[-1].strip(' ').split(' ')
            bugs_dict['Org_Summary'] = str1[-1].strip(' ')
            # bugs_dict['Labels'] = row[22:26]
            sample_bug_list.append(bugs_dict)
        return sample_bug_list


def read_values():
    # global feature
    # global summary
    feature=e1.get()
    summary=e2.get('1.0', END)
    user_input_bug = read_new_bug(feature, summary)
    find_duplicate_bugs(user_input_bug, featurewise_bug_list)
    master.quit()

# main program
stemmed_bug_list = removables(read_JIRA_file('JIRA.csv'))
featurewise_bug_list = (construct_feature_dictionary(stemmed_bug_list))


master = Tk()
Label(master, text="Feature: ", pady=10, padx=3).grid(row=0)
Label(master, text="Summary: ", pady=3, padx=3).grid(row=1)
e1 = Entry(master, width=50)
e2 = Text(master,width=38,height=3)

e1.grid(row=0, column=1)
e2.grid(row=1, column=1)

Button (master,text='Submit', command=read_values).grid(row=2,column=0,pady=5,sticky=W, padx=5)
Button (master,text='Close',command=master.quit).grid(row=2,column=1,pady=5,sticky=W)

mainloop( )



###########################################################
# for each_bug in featurewise_bug_list:
#     print removables(each_bug)
#         fp=open("dictionary.txt",'a')
#         fp.write(str(bugs_dict)+'\n')
#         fp.close()
#     csvfilereader.close()
# fp1=open("dictionary.txt",'r')
# for data in fp1:
#     sample_list.append(ast.literal_eval(data))
# print sample_list
# feature_list=[]
# feature_dict={}
# [feature_list.append(each_item['Feature']) for each_item in sample_list]
# for each_feature in list(set(feature_list)):
#     feature_dict['Feature']=each_feature
#     new_list=[]
#     for each_item in sample_list:
#         if each_feature==each_item['Feature']:
#             new_list.append({key:value for key,value in each_item.items() if key!='Feature'})
#
#     feature_dict['Details']=new_list
#     print removables(feature_dict)
#
# print read_new_bug()
# #         pickle.dump(sample_dict, fp)
# #         fp.close()

# def removables (list_of_dictionaries):
#     set_removables=set(['aboard', 'about', 'above', 'across', 'after', 'against', 'ahead of', 'along', 'amid',
# 'amidst', 'among', 'around', 'as', 'as far as', 'as of', 'aside from', 'at', 'athwart',
# 'atop','barring', 'because of', 'before', 'behind', 'below','beneath', 'beside', 'besides', 'between', 'beyond', 'but', 'by',
# 'by means of', 'circa', 'concerning','despite','down','during','except', 'except for', 'excluding', 'far from', 'following',
# 'for', 'from', 'in','in accordance with', 'in addition to', 'in case of', 'in front of', 'in lieu of', 'in place of',
# 'in spite of','including', 'inside',  'instead of', 'into', 'like', 'minus','near', 'next to', 'notwithstanding', 'of', 'off',
# 'on', 'on account of', 'on behalf of', 'on top of', 'onto','opposite', 'out', 'out of', 'outside', 'over', 'past', 'plus',
# 'prior to', 'regarding', 'regardless of', 'save', 'since', 'than', 'through', 'till', 'to','toward', 'towards','under',
# 'underneath', 'unlike', 'until', 'up', 'upon', 'versus', 'via', 'with', 'with regard to', 'within', 'without',
# ' ', 'if','is','are','was','were','a','an','the', 'then', 'like','there','it','that','here','and','','also',
# 'no','not','while','who','what','when','where','whom','whose'])
#     stemmer = Porter2Stemmer()
#     try:
#         for each_bug in list_of_dictionaries:
#             for eachitem in each_bug['Details']:
#                 #removing unwanted items from summary
#                 #applying stemming algorithm on each bug summary
#                 eachitem['Summary']=[stemmer.stem(i) for i in set(eachitem['Summary'])-set_removables]
#         return list_of_dictionaries
#     except:
#         list_of_dictionaries['Summary']=[stemmer.stem(i) for i in set(list_of_dictionaries['Summary'])-set_removables]
#         return list_of_dictionaries