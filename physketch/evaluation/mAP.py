'''
    CLASS INSPIRED BY https://github.com/Cartucho/mAP
'''
import glob
import json
import os
import shutil
from .utils import *

FORMAT_PHYD = 0
FORMAT_YOLO_JSON = 1


class mAP():

    def __init__(self, ground_truth_path, prediction_path, temp_path, results_path, ground_truth_format=FORMAT_PHYD,
                 prediction_format=FORMAT_YOLO_JSON, ground_truth_image_path=None, prediction_image_path=None,
                 save_plot=True,
                 class_ignore=[], MINOVERLAP=0.5, verbose=False):

        self.ap_dictionary = {}
        self.n_classes = 0
        self.class_ignore = class_ignore
        self.gt_classes = list()

        self.mAP = -1

        self.temp_path = os.path.normpath(temp_path)
        self.results_path = os.path.normpath(results_path)
        self.ground_truth_path = os.path.normpath(ground_truth_path)
        self.prediction_path = os.path.normpath(prediction_path)

        self.MINOVERLAP = MINOVERLAP

        self.ground_truth_ext = '.phyd' if ground_truth_format == FORMAT_PHYD else '.json'
        self.prediction_ext = '.phyd' if prediction_format == FORMAT_PHYD else '.json'

        self.ground_truth_format = ground_truth_format
        self.prediction_format = prediction_format

        assert ((
                        self.prediction_format == FORMAT_PHYD and prediction_image_path is not None) or self.prediction_format != FORMAT_PHYD)
        assert ((
                        self.ground_truth_format == FORMAT_PHYD and ground_truth_image_path is not None) or self.ground_truth_format != FORMAT_PHYD)

        self.ground_truth_image_path = ground_truth_image_path if self.ground_truth_format == FORMAT_PHYD else None
        self.prediction_image_path = prediction_image_path if self.prediction_format == FORMAT_PHYD else None

        self.gt_counter_per_class = {}

        self.predicted_files_list = []
        self.ground_truth_files_list = []
        self.pred_classes = []
        self.count_true_positives = {}
        self.pred_counter_per_class = {}

        self.verbose = verbose

        self._create_structure()
        self._read_ground_truth()
        self._read_predicted()
        self._calculate_AP()
        self._count_pred()

        if save_plot:
            self._draw_plot_ground_truth()
            self._draw_plot_predicted()
            self._draw_plot_mAP()

        self._write_results_ground_truth()
        self._write_results_predicted()

    def _create_structure(self):

        if not os.path.exists(self.temp_path):  # if it doesn't exist already
            os.makedirs(self.temp_path)

        if os.path.exists(self.results_path):  # if it exist already
            # reset the results directory
            shutil.rmtree(self.results_path)

        os.makedirs(self.results_path)
        os.makedirs(self.results_path + "/classes")

    def _read_ground_truth(self):
        gt_list = glob.glob(os.path.join(self.ground_truth_path, '*' + self.ground_truth_ext))
        gt_list.sort()
        # dictionary with counter per class

        i = 0
        for txt_file in gt_list:
            # print(txt_file)
            file_id = txt_file.split(".", 1)[0]
            file_id = os.path.basename(os.path.normpath(file_id))
            if not SampleParser.is_scene(file_id, image_dir=self.ground_truth_image_path,
                                         annotation_dir=self.ground_truth_path):
                continue
            # check if there is a correspondent predicted objects file
            if not os.path.exists(os.path.join(self.prediction_path, file_id + self.prediction_ext)):
                print("Warning. Prediction file not found: " + os.path.join(self.prediction_path, file_id + self.prediction_ext))
                continue
            i +=1
            self.ground_truth_files_list.append(txt_file)

            lines_list = normalize_file(txt_file, self.ground_truth_format, True,
                                        phy_image_dir=self.ground_truth_image_path,
                                        phy_annotation_dir=self.ground_truth_path)
            # create ground-truth dictionary
            bounding_boxes = []
            for line in lines_list:
                try:
                    class_name, left, top, right, bottom = line.split()
                    # check if class is in the ignore list, if yes skip
                    if class_name in self.class_ignore:
                        continue
                    bbox = left + " " + top + " " + right + " " + bottom
                    bounding_boxes.append({"class_name": class_name, "bbox": bbox, "used": False})
                    # count that object
                    if class_name in self.gt_counter_per_class:
                        self.gt_counter_per_class[class_name] += 1
                    else:
                        # if class didn't exist yet
                        self.gt_counter_per_class[class_name] = 1

                except ValueError:
                    error_msg = "Error: File " + txt_file + " in the wrong format.\n"
                    error_msg += " Expected: <class_name> <left> <top> <right> <bottom>\n"
                    error_msg += " Received: " + line
                    error_msg += "\n\nIf you have a <class_name> with spaces between words you should remove them\n"
                    error_msg += "by running the script \"rename_class.py\" in the \"extra/\" folder."
                    error(error_msg)

            # dump bounding_boxes into a ".json" file
            with open(os.path.join(self.temp_path, file_id + "_ground_truth.json"), 'w') as outfile:
                json.dump(bounding_boxes, outfile)

        gt_classes = list(self.gt_counter_per_class.keys())
        # let's sort the classes alphabetically
        self.gt_classes = sorted(gt_classes)
        self.n_classes = len(gt_classes)


        print("\t\t Ground truth samples: ",i)
        print("\t\t Ground truth classes: ",self.n_classes)


    def _read_predicted(self):
        pred_files_list = glob.glob(os.path.join(self.prediction_path, '*' + self.prediction_ext))
        pred_files_list.sort()

        for class_index, class_name in enumerate(self.gt_classes):

            bounding_boxes = []
            for txt_file in pred_files_list:
                # print(txt_file)
                # the first time it checks if all the corresponding ground-truth files exist
                file_id = txt_file.split(self.prediction_ext, 1)[0]
                file_id = os.path.basename(os.path.normpath(file_id))
                if class_index == 0:
                    if not os.path.exists(os.path.join(self.ground_truth_path, file_id + self.ground_truth_ext)):
                        error("Error. Ground Truth File not found: " + os.path.join(self.ground_truth_path, file_id + self.ground_truth_ext))

                self.predicted_files_list.append(txt_file)

                lines = normalize_file(txt_file, self.prediction_format, False,
                                       phy_image_dir=self.prediction_image_path,
                                       phy_annotation_dir=self.prediction_path)
                for line in lines:
                    try:
                        tmp_class_name, confidence, left, top, right, bottom = line.split()

                        if tmp_class_name == class_name:
                            # print("match")
                            bbox = left + " " + top + " " + right + " " + bottom
                            bounding_boxes.append({"confidence": confidence, "file_id": file_id, "bbox": bbox})
                    except ValueError:
                        error_msg = "Error: File " + txt_file + " in the wrong format.\n"
                        error_msg += " Expected: <class_name> <confidence> <left> <top> <right> <bottom>\n"
                        error_msg += " Received: " + line
                        error(error_msg)
                        # print(bounding_boxes)
            # sort predictions by decreasing confidence
            bounding_boxes.sort(key=lambda x: x['confidence'], reverse=True)

            with open(os.path.join(self.temp_path, class_name + "_predictions.json"), 'w') as outfile:
                json.dump(bounding_boxes, outfile)

    def _calculate_AP(self):

        # open file to store the results
        with open(self.results_path + "results.txt", 'w') as results_file:
            sum_AP = 0.0
            results_file.write("# AP and precision/recall per class\n")

            for class_index, class_name in enumerate(self.gt_classes):
                self.count_true_positives[class_name] = 0
                """
                 Load predictions of that class
                """
                predictions_file = os.path.join(self.temp_path, class_name + "_predictions.json")
                predictions_data = json.load(open(predictions_file))

                """
                 Assign predictions to ground truth objects
                """
                nd = len(predictions_data)
                tp = [0] * nd  # creates an array of zeros of size nd
                fp = [0] * nd
                for idx, prediction in enumerate(predictions_data):
                    file_id = prediction["file_id"]

                    '''if show_animation:
                        # find ground truth image
                        ground_truth_img = glob.glob1(img_path, file_id + ".*")
                        # tifCounter = len(glob.glob1(myPath,"*.tif"))
                        if len(ground_truth_img) == 0:
                            error("Error. Image not found with id: " + file_id)
                        elif len(ground_truth_img) > 1:
                            error("Error. Multiple image with id: " + file_id)
                        else:  # found image
                            # print(img_path + "/" + ground_truth_img[0])
                            # Load image
                            img = cv2.imread(img_path + "/" + ground_truth_img[0])
                            # Add bottom border to image
                            bottom_border = 60
                            BLACK = [0, 0, 0]
                            img = cv2.copyMakeBorder(img, 0, bottom_border, 0, 0, cv2.BORDER_CONSTANT, value=BLACK)'''

                    # assign prediction to ground truth object if any
                    #   open ground-truth with that file_id
                    gt_file = os.path.join(self.temp_path, file_id + "_ground_truth.json")
                    ground_truth_data = json.load(open(gt_file))
                    ovmax = -1
                    gt_match = -1
                    # load prediction bounding-box
                    bb = [float(x) for x in prediction["bbox"].split()]
                    for obj in ground_truth_data:
                        # look for a class_name match
                        if obj["class_name"] == class_name:
                            bbgt = [float(x) for x in obj["bbox"].split()]
                            bi = [max(bb[0], bbgt[0]), max(bb[1], bbgt[1]), min(bb[2], bbgt[2]), min(bb[3], bbgt[3])]
                            iw = bi[2] - bi[0] + 1
                            ih = bi[3] - bi[1] + 1
                            if iw > 0 and ih > 0:
                                # compute overlap (IoU) = area of intersection / area of union
                                ua = (bb[2] - bb[0] + 1) * (bb[3] - bb[1] + 1) + (bbgt[2] - bbgt[0]
                                                                                  + 1) * (
                                             bbgt[3] - bbgt[1] + 1) - iw * ih
                                ov = iw * ih / ua
                                if ov > ovmax:
                                    ovmax = ov
                                    gt_match = obj

                    # assign prediction as true positive or false positive
                    '''if show_animation:
                        status = "NO MATCH FOUND!"  # status is only used in the animation'''
                    # set minimum overlap
                    min_overlap = self.MINOVERLAP
                    # if specific_iou_flagged:
                    #    if class_name in specific_iou_classes:
                    #        index = specific_iou_classes.index(class_name)
                    #        min_overlap = float(iou_list[index])

                    if ovmax >= min_overlap:
                        if not bool(gt_match["used"]):
                            # true positive
                            tp[idx] = 1
                            gt_match["used"] = True
                            self.count_true_positives[class_name] += 1
                            # update the ".json" file
                            with open(gt_file, 'w') as f:
                                f.write(json.dumps(ground_truth_data))
                            # if show_animation:
                            #    status = "MATCH!"
                        else:
                            # false positive (multiple detection)
                            fp[idx] = 1
                            # if show_animation:
                            #    status = "REPEATED MATCH!"
                    else:
                        # false positive
                        fp[idx] = 1
                        if ovmax > 0:
                            status = "INSUFFICIENT OVERLAP"

                # print(tp)
                # compute precision/recall
                cumsum = 0
                for idx, val in enumerate(fp):
                    fp[idx] += cumsum
                    cumsum += val
                cumsum = 0
                for idx, val in enumerate(tp):
                    tp[idx] += cumsum
                    cumsum += val
                # print(tp)
                rec = tp[:]
                for idx, val in enumerate(tp):
                    rec[idx] = float(tp[idx]) / self.gt_counter_per_class[class_name]
                # print(rec)
                prec = tp[:]
                for idx, val in enumerate(tp):
                    prec[idx] = float(tp[idx]) / (fp[idx] + tp[idx])
                # print(prec)

                ap, mrec, mprec = voc_ap(rec, prec)
                sum_AP += ap
                text = "{0:.2f}%".format(
                    ap * 100) + " = " + class_name + " AP  "  # class_name + " AP = {0:.2f}%".format(ap*100)
                """
                 Write to results.txt
                """
                rounded_prec = ['%.2f' % elem for elem in prec]
                rounded_rec = ['%.2f' % elem for elem in rec]
                results_file.write(
                    text + "\n Precision: " + str(rounded_prec) + "\n Recall   :" + str(rounded_rec) + "\n\n")
                if self.verbose:
                    print(text)
                self.ap_dictionary[class_name] = ap

                """
                 Draw plot
                """

                plt.plot(rec, prec, '-o')
                plt.fill_between(mrec, 0, mprec, alpha=0.2, edgecolor='r')
                # set window title
                fig = plt.gcf()  # gcf - get current figure
                fig.canvas.set_window_title('AP ' + class_name)
                # set plot title
                plt.title('class: ' + text)
                # plt.suptitle('This is a somewhat long figure title', fontsize=16)
                # set axis titles
                plt.xlabel('Recall')
                plt.ylabel('Precision')
                # optional - set axes
                axes = plt.gca()  # gca - get current axes
                axes.set_xlim([0.0, 1.0])
                axes.set_ylim([0.0, 1.05])  # .05 to give some extra space
                # Alternative option -> wait for button to be pressed
                # while not plt.waitforbuttonpress(): pass # wait for key display
                # Alternative option -> normal display
                # plt.show()
                # save the plot
                fig.savefig(os.path.join(self.results_path, "classes", class_name + ".png"))
                plt.cla()# clear axes for next plot

                # if show_animation:
                #    cv2.destroyAllWindows()

            results_file.write("\n# mAP of all classes\n")
            mAP = sum_AP / self.n_classes
            text = "mAP = {0:.2f}%".format(mAP * 100)
            results_file.write(text + "\n")
            print("\t",text)
            self.mAP = mAP

        # remove the tmp_files directory
        shutil.rmtree(self.temp_path)

    def _count_pred(self):

        # all_classes_predicted_files = set([])
        for txt_file in self.predicted_files_list:
            # get lines to list
            lines = normalize_file(txt_file, self.prediction_format, False,
                                   phy_image_dir=self.prediction_image_path,
                                   phy_annotation_dir=self.prediction_path)
            for line in lines:
                class_name = line.split()[0]
                # check if class is in the ignore list, if yes skip
                if class_name in self.class_ignore:
                    continue
                # count that object
                if class_name in self.pred_counter_per_class:
                    self.pred_counter_per_class[class_name] += 1
                else:
                    # if class didn't exist yet
                    self.pred_counter_per_class[class_name] = 1
        # print(self.pred_counter_per_class)
        self.pred_classes = list(self.pred_counter_per_class.keys())
        for class_name in self.pred_classes:
            # if class exists in predictions but not in ground-truth then there are no true positives in that class
            if class_name not in self.gt_classes:
                self.count_true_positives[class_name] = 0

    def _draw_plot_ground_truth(self):
        window_title = "Ground-Truth Info"
        plot_title = "Ground-Truth\n"
        plot_title += "(" + str(len(self.ground_truth_files_list)) + " files and " + str(self.n_classes) + " classes)"
        x_label = "Number of objects per class"
        output_path = os.path.join(self.results_path, "Ground-Truth Info.png")
        to_show = False
        plot_color = 'forestgreen'
        draw_plot_func(
            self.gt_counter_per_class,
            self.n_classes,
            window_title,
            plot_title,
            x_label,
            output_path,
            to_show,
            plot_color,
            '',
        )

    def _draw_plot_predicted(self):
        window_title = "Predicted Objects Info"
        # Plot title
        plot_title = "Predicted Objects\n"
        plot_title += "(" + str(len(self.predicted_files_list)) + " files and "
        count_non_zero_values_in_dictionary = sum(int(x) > 0 for x in list(self.pred_counter_per_class.values()))
        plot_title += str(count_non_zero_values_in_dictionary) + " detected classes)"
        # end Plot title
        x_label = "Number of objects per class"
        output_path = os.path.join(self.results_path, "Predicted Objects Info.png")
        to_show = False
        plot_color = 'forestgreen'
        true_p_bar = self.count_true_positives
        draw_plot_func(
            self.pred_counter_per_class,
            len(self.pred_counter_per_class),
            window_title,
            plot_title,
            x_label,
            output_path,
            to_show,
            plot_color,
            true_p_bar
        )

    def _draw_plot_mAP(self, to_show=False, overwrite=True):

        window_title = "mAP"
        plot_title = "mAP = {0:.2f}%".format(self.mAP * 100)
        x_label = "Average Precision"
        output_path = os.path.join(self.results_path, "mAP.png")

        plot_color = 'royalblue'
        draw_plot_func(
            self.ap_dictionary,
            self.n_classes,
            window_title,
            plot_title,
            x_label,
            output_path,
            to_show,
            plot_color,
            ""
        )

    def _write_results_ground_truth(self):
        with open(os.path.join(self.results_path, "results.txt"), 'a') as results_file:
            results_file.write("\n# Number of ground-truth objects per class\n")
            for class_name in sorted(self.gt_counter_per_class):
                results_file.write(class_name + ": " + str(self.gt_counter_per_class[class_name]) + "\n")

    def _write_results_predicted(self):

        with open(os.path.join(self.results_path, "results.txt"), 'a') as results_file:
            results_file.write("\n# Number of predicted objects per class\n")
            for class_name in sorted(self.pred_classes):
                n_pred = self.pred_counter_per_class[class_name]
                text = class_name + ": " + str(n_pred)
                text += " (tp:" + str(self.count_true_positives[class_name]) + ""
                text += ", fp:" + str(n_pred - self.count_true_positives[class_name]) + ")\n"
                results_file.write(text)

'''
    mAP('/Users/zulli/Documents/PhySketch/Dataset/generated/annotated',
        '/Users/zulli/Documents/PhySketch/Dataset/generated/predict',
        '/Users/zulli/Documents/PhySketch/Dataset/generated/temp',
        '/Users/zulli/Documents/PhySketch/Dataset/generated/results',
        ground_truth_image_path='/Users/zulli/Documents/PhySketch/Dataset/generated/cropped')
'''