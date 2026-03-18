import com.google.gson.Gson;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;

import javax.swing.*;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;

public class BugSeverityFrontend {
    private static final String API_URL = "http://127.0.0.1:5000/predict"; // adjust if needed

    public static void main(String[] args) {
        SwingUtilities.invokeLater(BugSeverityFrontend::createAndShowGUI);
    }

    private static void createAndShowGUI() {
        JFrame frame = new JFrame("Bug Severity - Java Frontend");
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setSize(700, 480);

        JPanel panel = new JPanel(new GridBagLayout());
        GridBagConstraints gbc = new GridBagConstraints();
        gbc.insets = new Insets(6, 6, 6, 6);
        gbc.anchor = GridBagConstraints.WEST;
        gbc.fill = GridBagConstraints.HORIZONTAL;

        int row = 0;
        JTextField productField = addLabeledTextField(panel, "Product:", row++ , gbc);
        JTextField componentField = addLabeledTextField(panel, "Component:", row++ , gbc);
        JTextField resolutionField = addLabeledTextField(panel, "Resolution Category:", row++ , gbc);
        JTextField statusField = addLabeledTextField(panel, "Status Category:", row++ , gbc);
        JTextField votesField = addLabeledTextField(panel, "Quantity of Votes:", row++ , gbc);
        JTextField commentsField = addLabeledTextField(panel, "Quantity of Comments:", row++ , gbc);

        // Large description area
        JLabel descLabel = new JLabel("Full description:");
        gbc.gridx = 0; gbc.gridy = row; gbc.gridwidth = 1;
        panel.add(descLabel, gbc);
        JTextArea descArea = new JTextArea(8, 40);
        descArea.setLineWrap(true);
        descArea.setWrapStyleWord(true);
        JScrollPane scroll = new JScrollPane(descArea);
        gbc.gridx = 1; gbc.gridy = row++; gbc.gridwidth = 2; gbc.weightx = 1.0; gbc.fill = GridBagConstraints.BOTH;
        panel.add(scroll, gbc);
        gbc.fill = GridBagConstraints.HORIZONTAL; gbc.weightx = 0; gbc.gridwidth = 1;

        JButton submit = new JButton("Predict Severity");
        gbc.gridx = 0; gbc.gridy = row; gbc.gridwidth = 1;
        panel.add(submit, gbc);

        JButton clear = new JButton("Clear");
        gbc.gridx = 1; gbc.gridy = row; gbc.gridwidth = 1;
        panel.add(clear, gbc);

        submit.addActionListener((ActionEvent e) -> {
            submit.setEnabled(false);
            try {
                JsonObject payload = new JsonObject();
                payload.addProperty("product_name", productField.getText().trim());
                payload.addProperty("component_name", componentField.getText().trim());
                payload.addProperty("resolution_category", resolutionField.getText().trim());
                payload.addProperty("status_category", statusField.getText().trim());

                int votes = parseIntOrDefault(votesField.getText().trim(), 0);
                int comments = parseIntOrDefault(commentsField.getText().trim(), 0);
                payload.addProperty("quantity_of_votes", votes);
                payload.addProperty("quantity_of_comments", comments);

                payload.addProperty("full_description", descArea.getText().trim());

                String result = postJsonAndGetResult(API_URL, payload.toString());
                JOptionPane.showMessageDialog(frame, result, "Prediction Result", JOptionPane.INFORMATION_MESSAGE);

            } catch (Exception ex) {
                JOptionPane.showMessageDialog(frame, "Error: " + ex.getMessage(), "Error", JOptionPane.ERROR_MESSAGE);
            } finally {
                submit.setEnabled(true);
            }
        });

        clear.addActionListener(a -> {
            productField.setText("");
            componentField.setText("");
            resolutionField.setText("");
            statusField.setText("");
            votesField.setText("");
            commentsField.setText("");
            descArea.setText("");
        });

        frame.getContentPane().add(panel);
        frame.setLocationRelativeTo(null);
        frame.setVisible(true);
    }

    private static JTextField addLabeledTextField(JPanel panel, String label, int row, GridBagConstraints gbc) {
        JLabel l = new JLabel(label);
        gbc.gridx = 0; gbc.gridy = row; gbc.gridwidth = 1;
        panel.add(l, gbc);
        JTextField tf = new JTextField(40);
        gbc.gridx = 1; gbc.gridy = row; gbc.gridwidth = 2; gbc.weightx = 1.0;
        panel.add(tf, gbc);
        gbc.weightx = 0; gbc.gridwidth = 1;
        return tf;
    }

    private static int parseIntOrDefault(String s, int def) {
        try {
            if (s == null || s.isEmpty()) return def;
            return Integer.parseInt(s);
        } catch (Exception e) {
            return def;
        }
    }

    private static String postJsonAndGetResult(String urlString, String jsonPayload) throws Exception {
        URL url = new URL(urlString);
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        conn.setRequestMethod("POST");
        conn.setRequestProperty("Content-Type", "application/json; utf-8");
        conn.setRequestProperty("Accept", "application/json");
        conn.setDoOutput(true);

        try (OutputStream os = conn.getOutputStream()) {
            byte[] input = jsonPayload.getBytes("utf-8");
            os.write(input, 0, input.length);
        }

        int code = conn.getResponseCode();
        InputStreamReader isr = new InputStreamReader(code >= 400 ? conn.getErrorStream() : conn.getInputStream(), "utf-8");
        try (BufferedReader br = new BufferedReader(isr)) {
            StringBuilder response = new StringBuilder();
            String responseLine;
            while ((responseLine = br.readLine()) != null) {
                response.append(responseLine.trim());
            }
            String respStr = response.toString();
            // Try parsing JSON
            Gson gson = new Gson();
            JsonElement je = null;
            try {
                je = gson.fromJson(respStr, JsonElement.class);
            } catch (Exception ignore) {
            }
            if (je != null && je.isJsonObject()) {
                JsonObject obj = je.getAsJsonObject();
                // common keys: predicted_severity, severity, status
                if (obj.has("predicted_severity")) {
                    return "Predicted severity: " + obj.get("predicted_severity").getAsString();
                } else if (obj.has("severity")) {
                    return "Predicted severity: " + obj.get("severity").getAsString();
                } else if (obj.has("status") && obj.get("status").getAsString().equalsIgnoreCase("success") && obj.has("predicted_severity")) {
                    return "Predicted severity: " + obj.get("predicted_severity").getAsString();
                } else {
                    return "Response: " + obj.toString();
                }
            }
            return "Raw response: " + respStr;
        }
    }
}
