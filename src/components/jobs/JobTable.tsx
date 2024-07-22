import React, { useState } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Box,
  Typography,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Checkbox,
  Button,
} from "@mui/material";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";

interface stateProps {
    
}

interface Props {
  stateProps: stateProps;
}

export const JobTable = () => {
  return (
    <Table sx={{ tableLayout: "fixed", width: "100%" }}>
      <TableHead>
        <TableRow>
          <TableCell>Select</TableCell>
          <TableCell>Id</TableCell>
          <TableCell>Url</TableCell>
          <TableCell>Elements</TableCell>
          <TableCell>Result</TableCell>
          <TableCell>Time Created</TableCell>
          <TableCell>Status</TableCell>
          <TableCell>Actions</TableCell>
        </TableRow>
      </TableHead>
      <TableBody>
        {filteredJobs.map((row, index) => (
          <TableRow key={index}>
            <TableCell padding="checkbox">
              <Checkbox
                checked={selectedJobs.has(row.id)}
                onChange={() => handleSelectJob(row.id)}
              />
            </TableCell>
            <TableCell sx={{ maxWidth: 100, overflow: "auto" }}>
              <Box sx={{ maxHeight: 100, overflow: "auto" }}>{row.id}</Box>
            </TableCell>
            <TableCell sx={{ maxWidth: 200, overflow: "auto" }}>
              <Box sx={{ maxHeight: 100, overflow: "auto" }}>{row.url}</Box>
            </TableCell>
            <TableCell sx={{ maxWidth: 150, overflow: "auto" }}>
              <Box sx={{ maxHeight: 100, overflow: "auto" }}>
                {JSON.stringify(row.elements)}
              </Box>
            </TableCell>
            <TableCell sx={{ maxWidth: 150, overflow: "auto", padding: 0 }}>
              <Accordion sx={{ margin: 0, padding: 0.5 }}>
                <AccordionSummary
                  expandIcon={<ExpandMoreIcon />}
                  aria-controls="panel1a-content"
                  id="panel1a-header"
                  sx={{
                    minHeight: 0,
                    "&.Mui-expanded": { minHeight: 0 },
                  }}
                >
                  <Box
                    sx={{
                      maxHeight: 150,
                      overflow: "auto",
                      width: "100%",
                    }}
                  >
                    <Typography sx={{ fontSize: "0.875rem" }}>
                      Show Result
                    </Typography>
                  </Box>
                </AccordionSummary>
                <AccordionDetails sx={{ padding: 1 }}>
                  <Box sx={{ maxHeight: 200, overflow: "auto" }}>
                    <Typography
                      sx={{
                        fontSize: "0.875rem",
                        whiteSpace: "pre-wrap",
                      }}
                    >
                      {JSON.stringify(row.result, null, 2)}
                    </Typography>
                  </Box>
                </AccordionDetails>
              </Accordion>
            </TableCell>
            <TableCell sx={{ maxWidth: 150, overflow: "auto" }}>
              <Box sx={{ maxHeight: 100, overflow: "auto" }}>
                {new Date(row.time_created).toLocaleString()}
              </Box>
            </TableCell>
            <TableCell sx={{ maxWidth: 150, overflow: "auto" }}>
              <Box sx={{ maxHeight: 100, overflow: "auto" }}>
                <Box
                  className="rounded-md p-2 text-center"
                  sx={{ bgcolor: COLOR_MAP[row.status], opactity: "50%" }}
                >
                  {row.status}
                </Box>
              </Box>
            </TableCell>
            <TableCell sx={{ maxWidth: 100, overflow: "auto" }}>
              <Button
                onClick={() => {
                  handleDownload([row.id]);
                }}
              >
                Download
              </Button>
              <Button
                onClick={() =>
                  handleNavigate(row.elements, row.url, row.job_options)
                }
              >
                Rerun
              </Button>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
};
